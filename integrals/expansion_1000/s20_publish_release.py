"""Publish checked artifacts in the authorized data/model, test, report sequence."""
import argparse,hashlib,json,os,subprocess,time,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):return subprocess.check_output(args,cwd=str(ROOT)).decode().strip()
_storage_snapshot=None
def allocated(paths):
 return sum(int(line.split()[0]) for line in run(["du","-s","-B1"]+[str(p) for p in paths]).splitlines())
def guard():
 global _storage_snapshot
 # Dependencies finish every data/test/report writer before this process.
 # This publisher changes only .git and this phase's records/logs.
 mutable=allocated([ROOT/".git",HERE])
 if _storage_snapshot is None:
  remote=allocated([ROOT])
  _storage_snapshot=(remote,mutable)
 else:
  baseline,initial_mutable=_storage_snapshot
  # Never subtract reclaimed bytes; reserve a further 8 MiB for metadata.
  remote=baseline+max(0,mutable-initial_mutable)+8388608
 assert remote+200000000<9700000000,("Storage headroom bound",remote)
 return remote
def preflight(paths):
 # Loose Git blobs can approach source size, and directory trees/indexes also need space.
 current=guard();wanted=set(paths)
 names=set(run(["git","diff","--name-only","-z","HEAD","--"]+(["integrals","ML_model_seed_selection","ML_model_reduction","README.md","rules.md","report"])).split("\0"))
 names.update(run(["git","ls-files","--others","--exclude-standard","-z"]).split("\0"))
 bound=0;parents=set();count=0;selected=[]
 for name in names:
  if not name:continue
  parts=Path(name).parts
  if not any("/".join(parts[:i]) in wanted for i in range(1,len(parts)+1)):continue
  selected.append(name)
  p=ROOT/name
  if p.is_symlink():size=len(os.readlink(str(p)).encode())
  elif p.is_file():size=p.stat().st_size
  else:continue
  assert size<100*1024**2,("Oversized source blob",name,size)
  if not p.is_symlink() and p.suffix==".json" and size>1048576:
   compressor=zlib.compressobj(6)
   compressed=len(compressor.compress(("blob %d\0"%size).encode()))
   with p.open("rb") as f:
    for block in iter(lambda:f.read(1048576),b""):compressed+=len(compressor.compress(block))
   compressed+=len(compressor.flush())
   size=compressed
  size=(size*1002+999)//1000+128
  bound+=((size+4095)//4096)*4096;count+=1
  parents.update("/".join(parts[:i]) for i in range(1,len(parts)))
 bound+=4096*len(parents)+134217728
 assert current+200000000+bound<9700000000,("Insufficient pre-stage storage headroom",current,bound,count)
 print("Pre-stage storage bound",current,bound,count,flush=True)
 return current,bound,sorted(selected)
def stage_selected(names):
 # Restrict object creation to the files included in the pre-stage bound.
 if not names:return
 payload=("\0".join(names)+"\0").encode()
 subprocess.run(["git","--literal-pathspecs","-c","gc.auto=0","-c","core.looseCompression=6",
                 "add","-A","--pathspec-from-file=-","--pathspec-file-nul"],
                input=payload,cwd=str(ROOT),check=True)
def staged_bytes():
 staged=run(["git","diff","--cached","--name-only","--diff-filter=ACM"]).splitlines()
 total=0
 for name in staged:
  p=ROOT/name
  if p.is_file() and not p.is_symlink():
   size=p.stat().st_size
   assert size<100*1024**2,("Oversized Git blob",name,size)
   total+=size
 return total
def object_counts():
 return {line.split(":",1)[0]:int(line.split(":",1)[1]) for line in run(["git","count-objects","-v"]).splitlines() if ":" in line}
def compact_unpacked(commit):
 before=object_counts();record=dict(commit=commit,before=before)
 if before["count"]<1000 and before["size"]<16384:
  record["status"]="small_batch_left_loose"
 else:
  current=guard();temporary_bound=before["size"]*1024+67108864
  record.update(project_bytes_before=current,temporary_bound_bytes=temporary_bound)
  if current+200000000+temporary_bound>=9700000000:
   record["status"]="packing_skipped_to_preserve_temporary_headroom"
  else:
   subprocess.run(["git","-c","pack.threads=1","-c","pack.compression=6","-c","pack.windowMemory=64m","-c","pack.deltaCacheSize=16m","-c","gc.auto=0","repack","-d","-l","--window=0","--max-pack-size=256m"],cwd=str(ROOT),check=True)
   assert run(["git","rev-parse","HEAD"])==commit
   subprocess.run(["git","cat-file","-e","HEAD^{tree}"],cwd=str(ROOT),check=True)
   record.update(status="incremental_packing_complete",after=object_counts(),project_bytes_after=guard())
 path=HERE/"publication_packing.json";records=read(path) if path.exists() else []
 records.append(record);path.write_text(json.dumps(records,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print("Git storage",record["status"],flush=True)
def commit_staged(title):
 # Ordinary commit prefetches absent indexed blobs. Verify their published
 # references explicitly, then build the same tree without duplicating data.
 old=run(["git","rev-parse","HEAD"])
 branch=run(["git","symbolic-ref","HEAD"]);assert branch=="refs/heads/main"
 for key in ("core.hooksPath","commit.gpgSign"):
  value=subprocess.run(["git","config","--get",key],cwd=str(ROOT),stdout=subprocess.PIPE)
  assert value.returncode==1 or value.stdout.decode().strip().lower() in ("","false","no","0"),("Publication configuration requires review",key)
 hooks=Path(run(["git","rev-parse","--git-path","hooks"]))
 if not hooks.is_absolute():hooks=ROOT/hooks
 assert not [p.name for p in hooks.iterdir() if p.is_file() and not p.name.endswith(".sample") and os.access(str(p),os.X_OK)],"Active Git hooks require the normal commit workflow"
 remote=run(["git","ls-remote","origin","refs/heads/main"]).split()[0]
 subprocess.run(["git","merge-base","--is-ancestor",remote,old],cwd=str(ROOT),check=True)
 published={}
 for entry in run(["git","ls-tree","-r","-z",remote]).split("\0"):
  if not entry:continue
  header,path=entry.split("\t",1);mode,kind,oid=header.split()
  published[path]=(mode,oid)
 local=set(run(["git","cat-file","--batch-all-objects","--unordered","--batch-check=%(objectname)"]).splitlines())
 count=missing=0
 for entry in run(["git","ls-files","--stage","-z"]).split("\0"):
  if not entry:continue
  header,path=entry.split("\t",1);mode,oid,stage=header.split()
  assert stage=="0",("Unmerged index entry",path)
  count+=1
  if oid not in local:
   assert published.get(path)==(mode,oid),("Unpublished missing object",path,oid)
   missing+=1
 tree=run(["git","write-tree","--missing-ok"])
 commit=run(["git","commit-tree",tree,"-p",old,"-m",title])
 assert run(["git","rev-parse",commit+"^"])==old
 subprocess.run(["git","update-ref","-m",title,branch,commit,old],cwd=str(ROOT),check=True)
 assert run(["git","rev-parse","HEAD^{tree}"])==tree
 assert not run(["git","diff","--cached","--name-only"])
 path=HERE/"git_commit_integrity.json";checks=read(path) if path.exists() else []
 checks.append(dict(commit=commit,parent=old,published_parent=remote,index_entries=count,
                    absent_blobs_verified_against_published_paths=missing,tree=tree,
                    all_new_objects_local=True,history_rewritten=False))
 path.write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print("Verified partial-cache commit",commit,"published object references",missing,flush=True)
 return commit
def commit_and_push(title):
 commit=commit_staged(title)
 subprocess.run(["git","-c","pack.threads=1","-c","pack.window=0","-c","pack.windowMemory=64m","-c","pack.deltaCacheSize=16m","-c","gc.auto=0","push","origin","main"],cwd=str(ROOT),check=True)
 assert run(["git","ls-remote","origin","refs/heads/main"]).split()[0]==commit
 compact_unpacked(commit)
 return commit
def main():
 ap=argparse.ArgumentParser();ap.add_argument("stage",choices=["training","tests","report"]);args=ap.parse_args()
 assert os.environ.get("JOB_ID"),"Use a bounded compute allocation"
 evidence=read(HERE/"git_blob_estimate_validation.json")
 assert evidence["status"]=="passed" and evidence["publication_source_sha256"]==sha(Path(__file__))
 storage_check=read(HERE/"publication_storage_guard_validation.json")
 assert storage_check["status"]=="passed" and storage_check["publication_source_sha256"]==sha(Path(__file__))
 staging_check=read(HERE/"partial_clone_staging_validation.json")
 assert staging_check["status"]=="passed" and staging_check["publication_source_sha256"]==sha(Path(__file__))
 record=HERE/"publication.json";published=read(record) if record.exists() else {}
 if args.stage=="training":
  check=read(HERE/"training_release.json");assert check["status"]=="both_models_validated"
  for name,v in check["models"].items():assert sha(ROOT/name/"trained_model.pt")==v["model_sha256"]
  paths=["integrals","ML_model_seed_selection","ML_model_reduction","README.md","rules.md"]
  title="Add 1250 vacuum profiles per loop and continue both models for twenty passes"
 elif args.stage=="tests":
  assert "training" in published
  assert read(HERE/"test_release.json")["status"]=="both_frozen_tests_validated"
  paths=["integrals","ML_model_seed_selection","ML_model_reduction","README.md"]
  title="Publish frozen seed and reduction tests on 690382 held-out targets"
 else:
  assert "tests" in published and (ROOT/"report/report.pdf").is_file()
  paths=["report","integrals/expansion_1000","README.md","rules.md"]
  title="Report expanded integral construction and latest frozen model results"
 initial=guard()
 remote=run(["git","ls-remote","origin","refs/heads/main"]).split()[0]
 subprocess.run(["git","merge-base","--is-ancestor",remote,"HEAD"],cwd=str(ROOT),check=True)
 if args.stage=="training":
  # Each group stays well below GitHub's 2 GiB transfer bound.
  assert not run(["git","diff","--cached","--name-only"]),"Existing staged edits require inspection"
  if remote!=run(["git","rev-parse","HEAD"]):
   subprocess.run(["git","-c","pack.threads=1","-c","pack.window=0","-c","pack.windowMemory=64m","-c","pack.deltaCacheSize=16m","-c","gc.auto=0","push","origin","main"],cwd=str(ROOT),check=True)
  chunks=published.setdefault("family_groups",[])
  for first in (1,5,9):
   dirs=[]
   for kind in ("master_integrals","target_integrals","master_to_target"):
    base=ROOT/"integrals"/kind/"families"
    for loops in range(first,first+4):
     for p in sorted(base.glob("vacuum_L%02d_profile*"%loops)):
      if 101<=int(p.name.split("profile")[1])<=1350:dirs.append(str(p.relative_to(ROOT)))
   assert len(dirs)==15000,(first,len(dirs))
   completed=[g for g in chunks if g["first_loop"]==first and g["last_loop"]==first+3]
   if completed:
    assert len(completed)==1
    subprocess.run(["git","merge-base","--is-ancestor",completed[0]["commit"],"HEAD"],cwd=str(ROOT),check=True)
    # Check the immutable published family paths without generating or staging new copies.
    for start in range(0,len(dirs),500):
     batch=dirs[start:start+500]
     subprocess.run(["git","diff","--quiet",completed[0]["commit"],"--"]+batch,cwd=str(ROOT),check=True)
     assert not run(["git","ls-files","--others","--exclude-standard","--"]+batch),"Unexpected new family files"
    print("Verified previously published family group",first,first+3,flush=True)
    continue
   preflight(dirs)
   # Avoid the operating system's total argument-size bound.
   for start in range(0,len(dirs),500):
    subprocess.run(["git","-c","gc.auto=0","-c","core.looseCompression=6","add","-A","--"]+dirs[start:start+500],cwd=str(ROOT),check=True)
   if not run(["git","diff","--cached","--name-only"]):continue
   size=staged_bytes();assert size<1200000000,("Transfer batch too large",first,size)
   measured=guard()
   commit=commit_and_push("Add verified vacuum family records at loop orders %d through %d"%(first,first+3))
   chunks.append(dict(first_loop=first,last_loop=first+3,commit=commit,staged_source_bytes=size,project_bytes=measured))
   record.write_text(json.dumps(published,indent=2,sort_keys=True)+"\n",encoding="utf-8")
   print("Published family group",first,first+3,commit,flush=True)
 _,_,selected=preflight(paths)
 stage_selected(selected)
 actual_staged={name for name in run(["git","diff","--cached","--name-only","-z"]).split("\0") if name}
 assert actual_staged<=set(selected),"Unexpected staged edits outside the verified publication list"
 remaining=staged_bytes();assert remaining<1800000000,("Final transfer batch too large",remaining)
 after_stage=guard()
 commit=commit_and_push(title)
 published[args.stage]=dict(commit=commit,status="pushed",utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),project_bytes_before=initial,project_bytes_after_stage=after_stage,storage_accounting="One full allocated-size scan followed by conservative bounds from Git and publication-folder growth; 200 MB local allowance and 8 MiB metadata reserve")
 record.write_text(json.dumps(published,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps(published[args.stage]),flush=True)
if __name__=="__main__":main()
