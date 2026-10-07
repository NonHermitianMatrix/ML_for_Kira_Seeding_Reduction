"""Replace a redundant full Git object cache with a verified partial clone.

Working files, the existing index, refs and complete published commit history
remain unchanged. Run after both frozen tests and before test publication.
"""
import collections,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CACHE=ROOT/".tools/git-migration"
OLD=ROOT/".git";NEW=CACHE/"partial/.git";BACKUP=CACHE/"previous-metadata"
GIT="/u/local/apps/git/2.40.0/bin/git"
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS="0",GIT_TERMINAL_PROMPT="0")
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def git(where,*args,network=True):
 env=ENV if network else dict(ENV,GIT_SSH_COMMAND="false")
 return subprocess.check_output([GIT,"--git-dir="+str(where),"--work-tree="+str(ROOT)]+list(args),cwd=str(ROOT),env=env)
def refs(where):
 return dict(line.split(" ",1)[::-1] for line in git(where,"show-ref").decode().splitlines())
def objects(where):
 data=git(where,"cat-file","--batch-all-objects","--unordered","--batch-check=%(objectname) %(objecttype)",network=False).decode().splitlines()
 return collections.Counter(s.split()[1] for s in data),{s.split()[0] for s in data if s.endswith(" commit")}
def working_artifacts():
 paths=[ROOT/"README.md",ROOT/"rules.md",ROOT/".gitignore"]
 paths+=list((ROOT/"report").glob("*"))+list((ROOT/"report/figures").glob("*"))
 for model in ["ML_model_seed_selection","ML_model_reduction"]:
  folder=ROOT/model
  paths += [folder/name for name in ["trained_model.pt","trained_model.json","release_manifest.json"]]
  test=folder/"model_test"
  paths += [test/name for name in ["test_results.json","validation.json","family_metrics.json","prediction_manifest.json","figure_manifest.json"]]
 return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}

def allocated(where):return int(subprocess.check_output(["du","-s","-B1",str(where)]).split()[0])
def main():
 assert os.environ.get("JOB_ID"),"Use a bounded compute allocation"
 for name in ["ML_model_seed_selection","ML_model_reduction"]:
  assert read(ROOT/name/"model_test/validation.json")["status"]=="passed"
 assert OLD.is_dir() and NEW.is_dir() and not OLD.is_symlink() and not NEW.is_symlink() and not BACKUP.exists()
 for p in [OLD/"index.lock",OLD/"shallow",OLD/"objects/info/alternates",OLD/"worktrees",OLD/"modules"]:
  assert not p.exists(),str(p)
 assert list((NEW/"objects/pack").glob("*.promisor"))
 assert git(NEW,"config","--get","remote.origin.promisor").strip()==b"true"
 assert git(NEW,"config","--get","remote.origin.partialclonefilter").strip()==b"blob:none"
 head=git(OLD,"rev-parse","HEAD").strip()
 assert head==git(NEW,"rev-parse","HEAD").strip()
 assert head==git(OLD,"ls-remote","origin","refs/heads/main").split()[0]
 assert git(OLD,"rev-parse","HEAD^{tree}")==git(NEW,"rev-parse","HEAD^{tree}")
 oldrefs=refs(OLD);newrefs=refs(NEW)
 assert all(newrefs.get(k)==v for k,v in oldrefs.items())
 oldtypes,oldcommits=objects(OLD);newtypes,newcommits=objects(NEW)
 assert oldcommits<=newcommits,("Unpublished local commits",sorted(oldcommits-newcommits))
 assert newtypes["blob"]==0,("Prepared cache contains unexpected blobs",newtypes)
 assert git(OLD,"rev-list","--all","--count")==git(NEW,"rev-list","--all","--count")
 assert not git(OLD,"diff","--cached","--name-only","HEAD")
 index_hash=sha(OLD/"index")
 before_artifacts=working_artifacts()
 for name in ["index","config","description","COMMIT_EDITMSG","FETCH_HEAD","ORIG_HEAD"]:
  p=OLD/name
  if p.exists():shutil.copy2(str(p),str(NEW/name))
 for name in ["hooks","info","logs"]:
  p=OLD/name
  if p.exists():
   dest=NEW/name
   if dest.exists():shutil.rmtree(str(dest))
   shutil.copytree(str(p),str(dest))
 for key,value in [("core.repositoryformatversion","1"),("remote.origin.promisor","true"),
                   ("remote.origin.partialclonefilter","blob:none"),("gc.auto","0"),("diff.renames","false"),("core.checkStat","minimal")]:
  git(NEW,"config",key,value)
 assert sha(NEW/"index")==index_hash
 assert git(NEW,"diff","--cached","--name-only","HEAD")==b""
 assert sha(OLD/"index")==index_hash
 before_bytes=allocated(ROOT);old_object_bytes=allocated(OLD/"objects")
 # Removal must reclaim these objects, rather than leave another hard link.
 for directory,dirs,files in os.walk(str(OLD/"objects")):
  for name in files:assert (Path(directory)/name).stat().st_nlink==1
 assert before_bytes+200000000<9700000000,("Project headroom",before_bytes)
 print("Verified matching HEAD, tree, refs, all local commits, index and current artifact hashes.",flush=True)
 OLD.rename(BACKUP)
 try:
  NEW.rename(OLD)
  assert git(OLD,"rev-parse","HEAD").strip()==head
  assert sha(OLD/"index")==index_hash and working_artifacts()==before_artifacts
  assert all(refs(OLD).get(k)==v for k,v in oldrefs.items())
 except BaseException:
  if OLD.exists():OLD.rename(NEW)
  BACKUP.rename(OLD)
  raise
 # Only the redundant Git object cache is removed after verification.
 # All working data, model weights and tests remain outside .git.
 shutil.rmtree(str(BACKUP/"objects"))
 # The only following storage change removes the measured, singly linked
 # object tree. Reserve 64 MiB for directory and audit-record metadata.
 after_bound=before_bytes-old_object_bytes+67108864
 assert after_bound+200000000<9700000000
 record=dict(status="verified_partial_git_cache_active",utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
  head=head.decode(),old_object_types=dict(oldtypes),new_object_types=dict(newtypes),
  all_local_commits_preserved=len(oldcommits),all_refs_preserved=oldrefs,index_sha256=index_hash,
  working_artifact_sha256=before_artifacts,
  project_bytes_before=before_bytes,project_bytes_after_upper_bound=after_bound,
  removed_redundant_object_bytes=old_object_bytes,
  working_files_unchanged=True,mutation_scope="Only Git metadata and ignored Git caches; no working data/model/test/report paths are written",history_rewritten=False,metadata_backup=str(BACKUP.relative_to(ROOT)),
  git_version=git(OLD,"--version").decode().strip(),
  documentation="https://git-scm.com/docs/partial-clone",
  note="Use module load git/2.40.0 on Hoffman. Missing historical blobs remain on GitHub and are retrieved only when needed.")
 (HERE/"git_cache_refresh.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps(record),flush=True)
if __name__=="__main__":main()
