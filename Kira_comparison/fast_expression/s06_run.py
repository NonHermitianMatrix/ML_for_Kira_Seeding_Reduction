"""Rotate complete cold trials and retain failures within fixed resource limits."""
import argparse,gzip,hashlib,json,os,pathlib,platform,resource,shutil,signal,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];ACC=HERE.parent/"acceleration"
sys.path[:0]=[str(ACC),str(HERE.parent)]
from s03_run import rss_tree,allocated
import s36_evidence as archive
archive.HERE=HERE
from s13_records import compact
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+"\n")
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(1900000000,)*2)
 resource.setrlimit(resource.RLIMIT_FSIZE,(33554432,)*2)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--partition",choices=["development","test"],required=True)
 ap.add_argument("--case",type=int,required=True);ap.add_argument("--size",type=int,required=True)
 ap.add_argument("--repetitions",type=int,default=1);a=ap.parse_args()
 plan=json.loads((HERE/"plan.json").read_text());policies=plan["policies"]
 if a.partition=="test":
  freeze=json.loads((HERE/"freeze.json").read_text())
  for name,h in freeze["sha256"].items():assert sha(ROOT/name)==h,name
  assert a.repetitions==plan["repetitions"] and a.size in plan["target_sizes"]
 out=HERE/a.partition;out.mkdir(exist_ok=True);work=pathlib.Path(os.environ["KIRA_FAST_SCRATCH"])
 prefix=f"{a.partition}_{a.case:02d}_n{a.size}"
 write(out/("environment_"+prefix+".json"),dict(host=platform.node(),cpu=next(x.split(":",1)[1].strip() for x in pathlib.Path("/proc/cpuinfo").read_text().splitlines() if x.startswith("model name")),plan_sha256=sha(HERE/"plan.json")))
 prior_failed={}
 for rep in range(a.repetitions):
  k=(a.case+rep)%len(policies)
  for policy in policies[k:]+policies[:k]:
   name=f"{prefix}_r{rep}_{policy}";dest=out/(name+".json.gz")
   assert not dest.exists(),dest
   if policy in prior_failed:
    result=dict(trial=name,partition=a.partition,case=a.case,size=a.size,repetition=rep,policy=policy,
     success=False,status="skipped_after_failure",measured=False,cold_seconds=None,trigger=prior_failed[policy])
   else:
    if allocated(HERE)>plan["retained_limit_bytes"]:raise RuntimeError("Retained output limit")
    if shutil.disk_usage(work).free<150000000:raise RuntimeError("Scratch headroom")
    scratch=work/name;scratch.mkdir();record=scratch/"record.json";peak=0;diskpeak=0;reason=None;t=time.perf_counter()
    with (scratch/"worker.log").open("w") as log:
     p=subprocess.Popen([str(ROOT/".tools/seed-model/venv/bin/python"),str(HERE/"s05_worker.py"),
      a.partition,str(a.case),str(a.size),policy,str(scratch),str(record)],stdout=log,stderr=subprocess.STDOUT,
      start_new_session=True,preexec_fn=limits)
     nextdisk=0.;nextmem=0.
     while p.poll() is None:
      elapsed=time.perf_counter()-t
      if elapsed>=nextmem:peak=max(peak,rss_tree(p.pid));nextmem=elapsed+.05
      if elapsed>=nextdisk:diskpeak=max(diskpeak,allocated(scratch));nextdisk=elapsed+.5
      if elapsed>plan["timeout_seconds"]:reason="timeout"
      if peak>plan["rss_limit_bytes"]:reason="rss_limit"
      if diskpeak>plan["scratch_limit_bytes"]:reason="scratch_limit"
      if reason:
       os.killpg(p.pid,signal.SIGTERM)
       try:p.wait(timeout=2)
       except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
       break
      time.sleep(.01)
    elapsed=time.perf_counter()-t
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    result=json.loads(record.read_text()) if record.exists() else {"success":False}
    result.update(trial=name,partition=a.partition,case=a.case,size=a.size,repetition=rep,policy=policy,measured=True,
     cold_seconds=elapsed,peak_rss_bytes=peak,scratch_peak_bytes=diskpeak,returncode=p.returncode,
     status=reason or ("completed" if p.returncode==0 else "error"),worker_sha256=sha(HERE/"s05_worker.py"))
    evidence={}
    for path in scratch.rglob("*"):
     if path.is_file() and path.name in ["worker.log","run.log","jobs.yaml","kira_targets.kira"]:
      evidence[str(path.relative_to(scratch))]=path.read_text(errors="replace")
    result["evidence"]=archive.pack(evidence)
    shutil.rmtree(scratch)
    if not result["success"] or result["status"]!="completed":prior_failed[policy]=name
   with gzip.open(dest,"wt",encoding="utf-8",compresslevel=9) as stream:json.dump(compact(result),stream,separators=(",",":"),allow_nan=False)
   print(json.dumps({k:result[k] for k in ["trial","cold_seconds","status","success"]}),flush=True)
 write(out/("complete_"+prefix+".json"),dict(completed=True,trials=a.repetitions*len(policies)))
if __name__=="__main__":main()
