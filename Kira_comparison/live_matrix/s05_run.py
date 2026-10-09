"""Counterbalanced trials with hard time, memory, scratch and output bounds."""
import argparse,gzip,json,os,pathlib,platform,resource,shutil,signal,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s03_run import rss_tree,allocated
def write(p,x):p.write_text(json.dumps(x,indent=2)+"\n")
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(1900000000,1900000000))
 resource.setrlimit(resource.RLIMIT_FSIZE,(33554432,33554432))
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--case",type=int,required=True)
 ap.add_argument("--pilot",action="store_true");args=ap.parse_args()
 plan=json.load(open(HERE/"plan.json"))
 out=HERE/("pilot" if args.pilot else "results");out.mkdir(exist_ok=True)
 work=pathlib.Path(os.environ["KIRA_LIVE_SCRATCH"])
 policies=plan["policies"];trials=[]
 for rep in range(1 if args.pilot else 3):
  rotate=(args.case+rep)%len(policies)
  for policy in policies[rotate:]+policies[:rotate]:trials.append((rep,policy))
 write(out/("environment_%02d.json"%args.case),dict(host=platform.node(),case=args.case,
      cpu=next(x.split(":",1)[1].strip() for x in pathlib.Path("/proc/cpuinfo").read_text().splitlines() if x.startswith("model name")),
      plan_sha256=__import__("hashlib").sha256((HERE/"plan.json").read_bytes()).hexdigest()))
 for number,(rep,policy) in enumerate(trials):
  name="%02d_r%d_%s"%(args.case,rep,policy);dest=out/(name+".json.gz")
  if dest.exists():continue
  total=allocated(HERE)
  if total>128000000 or plan["prior_storage_upper_bytes"]+4*total+160000000>=10000000000:
   raise RuntimeError("Project storage headroom guard")
  if shutil.disk_usage(work).free<250000000:raise RuntimeError("Scratch headroom")
  scratch=work/name;scratch.mkdir();record=scratch/"record.json";peak=0;diskpeak=0;reason=None
  t=time.perf_counter()
  with (scratch/"worker.log").open("w") as log:
   p=subprocess.Popen([str(ROOT/".tools/seed-model/venv/bin/python"),str(HERE/"s04_worker.py"),
       str(args.case),policy,str(scratch),str(record)],stdout=log,stderr=subprocess.STDOUT,
       start_new_session=True,preexec_fn=limits)
   nextdisk=0.
   while p.poll() is None:
    elapsed=time.perf_counter()-t;peak=max(peak,rss_tree(p.pid))
    if elapsed>=nextdisk:diskpeak=max(diskpeak,allocated(scratch));nextdisk=elapsed+.5
    if elapsed>plan["timeout_seconds"]:reason="timeout"
    if peak>1700000000:reason="rss_limit"
    if diskpeak>64000000:reason="scratch_limit"
    if reason:
     os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=2)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
     break
    time.sleep(.05)
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  result=json.load(open(record)) if record.exists() else {"success":False}
  result.update(trial=name,case=args.case,repetition=rep,policy=policy,cold_seconds=time.perf_counter()-t,
      peak_rss_bytes=peak,scratch_peak_bytes=diskpeak,returncode=p.returncode,
      status=reason or ("completed" if p.returncode==0 else "error"))
  evidence={}
  for path in scratch.rglob("*"):
   if not path.is_file():continue
   if path.name in ["worker.log","run.log","jobs.yaml","integralfamilies.yaml","kinematics.yaml",
                     "kira_targets.kira","context.json","forward.jsonl","row_trace.txt"]:
    evidence[str(path.relative_to(scratch))]=path.read_text(errors="replace")
   if path.name.endswith(".policy.jsonl.gz"):
    with gzip.open(path,"rt") as stream:evidence[str(path.relative_to(scratch))]=stream.read()
  result["evidence"]=evidence
  with gzip.open(dest,"wt",encoding="utf-8") as stream:json.dump(result,stream,separators=(",",":"),allow_nan=False)
  shutil.rmtree(scratch)
  write(out/("status_%02d.json"%args.case),dict(completed=number+1,total=len(trials),
       last_trial=name,success=result["success"],status=result["status"]))
  print(json.dumps({k:result[k] for k in ["trial","cold_seconds","status","success"]}),flush=True)
 write(out/("complete_%02d.json"%args.case),dict(trials=len(trials),completed=True))
if __name__=="__main__":main()

