"""Check the previously slow native combination and the learned native envelope."""
from s01_common import *
import subprocess,signal,shutil
from s03_run import limits,rss_tree,allocated
def main():
 out=HERE/"native_regression";out.mkdir(exist_ok=True)
 work=pathlib.Path(os.environ["KIRA_COMPARISON_SCRATCH"])
 tests=[("s02_worker.py",1,"kira_native"),("s02_worker.py",16,"kira_native_trim"),
        ("s10_native_worker.py",16,"ml_native_seeds")]
 for script,size,policy in tests:
  dest=out/(policy+".json.gz")
  if dest.exists():continue
  scratch=work/policy;scratch.mkdir();record=scratch/"record.json";peak=0;reason=None;start=time.perf_counter()
  with (scratch/"worker.log").open("w") as log:
   p=subprocess.Popen([str(ROOT/".tools/seed-model/venv/bin/python"),str(HERE/script),"0",str(size),policy,str(scratch),str(record)],
    stdout=log,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits)
   while p.poll() is None:
    peak=max(peak,rss_tree(p.pid))
    if time.perf_counter()-start>180:reason="timeout"
    if allocated(scratch)>33554432:reason="scratch_limit"
    if peak>1400000000:reason="rss_limit"
    if reason:os.killpg(p.pid,signal.SIGKILL);p.wait();break
    time.sleep(.1)
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  result=read(record) if record.exists() else {"success":False}
  result.update(resource_status=reason or ("completed" if p.returncode==0 else "error"),
   cold_seconds=time.perf_counter()-start,peak_rss=peak)
  result["logs"]={str(f.relative_to(scratch)):f.read_text(errors="replace") for f in scratch.rglob("*.log")}
  with gzip.open(dest,"wt") as f:json.dump(result,f)
  shutil.rmtree(scratch)
  print(json.dumps(dict(policy=policy,status=result["resource_status"],success=result["success"],seconds=result["cold_seconds"])),flush=True)
 write(out/"complete.json",dict(completed=True))
if __name__=="__main__":main()
