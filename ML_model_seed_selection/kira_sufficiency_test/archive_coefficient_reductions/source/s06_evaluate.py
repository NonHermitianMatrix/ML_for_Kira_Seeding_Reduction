"""Freeze the solver protocol and evaluate disjoint held-out systems on Hoffman."""
import argparse,collections,gzip,shutil,socket,time,traceback,io,contextlib
from s03_kira_adapter import *
from s08_verify import check_records
POLICIES=("predicted","full","background")
def protocol():
 pilot=read(HERE/"pilot/summary.json")
 assert len(pilot["families"])==5
 assert all(not f.get("error") and f["counts"]["full"]=={"exact_match":f["targets"]} for f in pilot["families"])
 assert sha(MODEL/"trained_model.pt")==EXPECTED_MODEL
 assert sha(MODEL/"split_manifest.json")==EXPECTED_SPLIT
 pm=read(MODEL/"model_test/prediction_manifest.json")
 assert pm["model_sha256"]==EXPECTED_MODEL and pm["split_sha256"]==EXPECTED_SPLIT
 metas=[f for f in read(MODEL/"split_manifest.json")["families"] if f["split"]=="test"]
 value=dict(schema_version=1,model_sha256=EXPECTED_MODEL,split_sha256=EXPECTED_SPLIT,threshold=0.5,
  prediction_manifest_sha256=sha(MODEL/"model_test/prediction_manifest.json"),
  kira_sha256=sha(ROOT/".tools/kira/bin/kira"),fermat_sha256=sha(ROOT/".tools/Ferl7/fer64"),
  kira_version="3.1",mode="symbolic user-defined systems; Fermat; no FireFly",
  reference_use="Post-solve comparison only; no reference equations or labels supplied to Kira",
  family_ids=[m["family"] for m in metas],families=len(metas),targets=sum(m["counts"]["targets"] for m in metas),
  policies=list(POLICIES),workers=16,batch_equation_limit=50000,
  timeout_seconds=600,scratch_per_worker_bytes=67108864,
  persisted_per_worker_bytes=25165824,local_allowance_bytes=250000000,
  project_limit_bytes=10000000000,
  source_commit="04ae8f062a342602e02f79d95c1dc52a3e616f28",
  scripts={name:sha(HERE/name) for name in ["s02_common.py","s03_kira_adapter.py","s06_evaluate.py","s08_verify.py"]},
  storage_upper_bound_including_all_reserves_bytes=9656690304,
  storage_baseline=".tools/report-conclusion/storage_before_build.json")
 write(HERE/"protocol.json",value);return value
@contextlib.contextmanager
def bounded_gzip(path,binary=False):
 tmp=path.with_name(path.name+".part")
 remaining=25165824-allocated(path.parent)-8192
 assert remaining>0,"Worker output reserve reached"
 class Sink:
  def __init__(self,f):self.f=f;self.left=remaining
  def write(self,b):
   if len(b)>self.left:raise RuntimeError("Worker compressed-output reserve reached")
   n=self.f.write(b);self.left-=n;return n
  def flush(self):self.f.flush()
 try:
  with tmp.open("wb") as raw:
   with gzip.GzipFile(fileobj=Sink(raw),mode="wb",compresslevel=6,mtime=0) as compressed:
    if binary:yield compressed
    else:
     with io.TextIOWrapper(compressed,encoding="utf-8") as text:yield text
  os.replace(str(tmp),str(path))
 except BaseException:
  if tmp.exists():tmp.unlink()
  raise
def save_gz(path,value):
 with bounded_gzip(path) as f:json.dump(value,f,separators=(",",":"),allow_nan=False)
def process(meta,prediction_entry,dest,scratch):
 start=time.monotonic();family=load_family(meta,prediction_entry);blocks=selected_blocks(family)
 counts={p:collections.Counter() for p in POLICIES};target_results={};batchinfo=[];sourcehash={}
 for k in ["definition","masters","inputs","seeds","references"]:
  sourcehash[k]=sha(DATA/meta[k])
 refs=None
 for j,batch in enumerate(batches(blocks)):
  w=scratch/("case_%03d"%j)
  if w.exists():shutil.rmtree(w)
  manifest=export(family,batch,w);run=run_kira(w)
  if run["status"]!="completed":
   # Preserve the failed job's bounded input and log for diagnosis.
   failure=dest/(meta["family"]+"_failure")
   failure.mkdir(exist_ok=True)
   for name in ["system.kira","targets","masters","jobs.yaml","run.log"]:
    shutil.copyfile(str(w/name),str(failure/name))
   write(failure/"manifest.json",manifest);write(failure/"run.json",run)
   raise RuntimeError(str(run))
  if refs is None:refs={x["id"]:x for x in rows(DATA/meta["references"])}
  outpath=w/"results/Tuserweight/kira_targets.kira"
  records=assess(family,manifest,parse_output(outpath),refs)
  run["independent_sample_checks"]=check_records(records,refs)
  byblock={b["id"]:b for b in manifest["blocks"]}
  for rec in records:
   for policy,tids in byblock[rec["block"]]["policies"].items():
    if rec["target"] in tids:
     counts[policy][rec["status"]]+=1
     target_results.setdefault(rec["target"],{})[policy]=rec["status"]
  stem=meta["family"]+"_%03d"%j
  detail=dest/(stem+".json.gz");raw=dest/(stem+".kira.gz")
  save_gz(detail,dict(manifest=manifest,run=run,records=records))
  with outpath.open("rb") as inp,bounded_gzip(raw,binary=True) as out:shutil.copyfileobj(inp,out)
  batchinfo.append(dict(detail=detail.name,detail_sha256=sha(detail),output=raw.name,output_sha256=sha(raw),run=run,
                        equations=manifest["equations"],columns=manifest["columns"]))
  shutil.rmtree(w)
  clear_caches()
 pertarget=[]
 byid={t["id"]:t for t in family["targets"]}
 masks={tid:len(b["mask"]) for b in blocks for tid in b["policies"]["predicted"]}
 for tid,states in target_results.items():
  assert set(states)==set(POLICIES)
  pertarget.append(dict(target=tid,kind=byid[tid]["kind"],selected_seeds=masks[tid],candidate_seeds=len(family["seeds"]),**states))
 assert len(pertarget)==len(family["targets"])
 assert all(sum(c.values())==len(pertarget) for c in counts.values())
 result=dict(family=meta["family"],loops=meta["loops"],targets=len(pertarget),selection_groups=len(blocks),
  counts={p:dict(c) for p,c in counts.items()},target_results=pertarget,batches=batchinfo,
  prediction_sha256=family["prediction_sha256"],source_sha256=sourcehash,
  identities_sha256=sha(family_file(meta["family"],"identities.jsonl.gz")),seconds=time.monotonic()-start,
  host=socket.gethostname())
 save_gz(dest/(meta["family"]+".summary.json.gz"),result)
 return result
def worker(index):
 config=read(HERE/"protocol.json")
 assert sha(MODEL/"trained_model.pt")==config["model_sha256"] and sha(MODEL/"split_manifest.json")==config["split_sha256"]
 assert sha(ROOT/".tools/kira/bin/kira")==config["kira_sha256"]
 metas={m["family"]:m for m in read(MODEL/"split_manifest.json")["families"]}
 entries={e["family"]:e for e in read(MODEL/"model_test/prediction_manifest.json")["families"]}
 selected=config["family_ids"][index::config["workers"]]
 dest=HERE/"results"/("worker_%02d"%index);dest.mkdir(parents=True,exist_ok=True)
 scratch=Path(os.environ.get("KIRA_SCRATCH",str(WORK)))/("worker_%02d"%index);scratch.mkdir(parents=True,exist_ok=True)
 assert shutil.disk_usage(str(scratch)).free>2*config["scratch_per_worker_bytes"]
 memory={line.split(":")[0]:int(line.split()[1]) for line in Path("/proc/meminfo").read_text().splitlines()}
 assert memory["MemAvailable"]>3*1024*1024,"Insufficient compute-node memory headroom"
 status=dict(worker=index,assigned=len(selected),completed=0,errors=[],families=[])
 try:
  for fid in selected:
   clear_caches()
   if allocated(dest)>config["persisted_per_worker_bytes"]:raise RuntimeError("Worker output reserve reached")
   output=dest/(fid+".summary.json.gz")
   if output.exists():
    result=json.loads(gzip.open(str(output),"rt",encoding="utf-8").read())
    assert result["prediction_sha256"]==entries[fid]["sha256"]
    assert all(sha(dest/b["detail"])==b["detail_sha256"] and sha(dest/b["output"])==b["output_sha256"] for b in result["batches"])
   else:
    result=process(metas[fid],entries[fid],dest,scratch)
   status["completed"]+=1;status["families"].append(fid)
   status["last_family"]=fid;status["allocated_bytes"]=allocated(dest)
   write(HERE/("worker_%02d.json"%index),status)
   print(json.dumps(dict(worker=index,family=fid,seconds=result["seconds"],counts=result["counts"])),flush=True)
 except Exception:
  status["errors"].append(traceback.format_exc());write(HERE/("worker_%02d.json"%index),status);raise
 status["finished"]=True;write(HERE/("worker_%02d.json"%index),status)
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--freeze",action="store_true");parser.add_argument("--worker",type=int)
 args=parser.parse_args()
 if args.freeze:protocol()
 else:worker(args.worker)
