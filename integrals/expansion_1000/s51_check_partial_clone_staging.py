"""Check bounded staging in a blob-filtered clone without fetching unchanged data."""
import hashlib,importlib.util,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def git(root,*args,**kw):
 return subprocess.check_output(["git"]+list(args),cwd=str(root),**kw)
def objects(root):
 return set(git(root,"cat-file","--batch-all-objects","--unordered","--batch-check=%(objectname)",stderr=subprocess.DEVNULL).decode().splitlines())
def main():
 spec=importlib.util.spec_from_file_location("publisher",HERE/"s20_publish_release.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 with tempfile.TemporaryDirectory(prefix="partial-staging-check-",dir=str(ROOT/".tools")) as name:
  base=Path(name);origin=base/"origin";work=base/"work";server=base/"server.git";origin.mkdir()
  git(origin,"init","-q","--initial-branch=main")
  for k,v in [("user.name","Publication Check"),("user.email","check@example.invalid"),("uploadpack.allowFilter","true"),("gc.auto","0")]:
   git(origin,"config",k,v)
  (origin/"integrals").mkdir();(origin/"report").mkdir()
  (origin/"integrals/immutable.bin").write_bytes(bytes(range(256))*4096)
  (origin/"report/report.tex").write_text("old report\n")
  (origin/"report/old.txt").write_text("remove this fixture file\n")
  git(origin,"add",".");git(origin,"commit","-qm","Fixture baseline")
  immutable=git(origin,"rev-parse","HEAD:integrals/immutable.bin").decode().strip()
  git(base,"clone","-q","--bare",str(origin),str(server))
  git(server,"config","uploadpack.allowFilter","true")
  git(base,"-c","protocol.file.allow=always","clone","-q","--filter=blob:none","--no-checkout",server.as_uri(),str(work))
  (work/"integrals").mkdir();shutil.copytree(str(origin/"report"),str(work/"report"))
  os.link(str(origin/"integrals/immutable.bin"),str(work/"integrals/immutable.bin"))
  git(origin,"update-index","--refresh")
  shutil.copy2(str(origin/".git/index"),str(work/".git/index"))
  git(work,"config","core.checkStat","minimal");git(work,"config","diff.renames","false")
  git(work,"config","user.name","Publication Check");git(work,"config","user.email","check@example.invalid")
  git(work,"config","gc.auto","0");git(work,"config","pack.threads","1")
  (work/"report/report.tex").write_text("new report with a changed value\n")
  (work/"report/old.txt").unlink();(work/"report/new [note].txt").write_text("new fixture record\n")
  assert immutable not in objects(work)
  mod.ROOT=work;mod.HERE=work/"integrals/expansion_1000";mod.HERE.mkdir();mod._storage_snapshot=None
  _,_,selected=mod.preflight(["integrals","report"])
  expected={"report/report.tex","report/old.txt","report/new [note].txt"}
  assert set(selected)==expected,selected
  mod.stage_selected(selected)
  staged=set(git(work,"diff","--cached","--name-only","-z").decode().strip("\0").split("\0"))
  assert staged==expected,staged
  assert git(work,"show",":report/report.tex")==b"new report with a changed value\n"
  assert immutable not in objects(work),"Unchanged integral blob was fetched or restaged"
  commit=mod.commit_and_push("Fixture checked release")
  assert git(server,"rev-parse","refs/heads/main").decode().strip()==commit
  git(server,"fsck","--full")
  assert immutable not in objects(work),"Push downloaded an unchanged integral blob"
  git(work,"-c","pack.threads=1","repack","-d","-l","--window=0")
  assert immutable not in objects(work),"Repacking downloaded an unchanged integral blob"
  result=dict(status="passed",staged_paths=sorted(staged),unchanged_integral_blob_remains_absent=True,
              commit_push_repack_and_complete_server_integrity_checked=True,
              changed_new_deleted_and_literal_paths_checked=True,temporary_fixture_removed=True,
              publication_source_sha256=hashlib.sha256((HERE/"s20_publish_release.py").read_bytes()).hexdigest())
 (HERE/"partial_clone_staging_validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
