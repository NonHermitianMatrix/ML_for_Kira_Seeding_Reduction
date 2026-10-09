"""Counterbalanced complete trials, with bounded time, memory and scratch."""
import argparse,gzip,hashlib,json,os,pathlib,platform,resource,shutil,signal,subprocess,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from s03_run import rss_tree,allocated
from s36_evidence import pack
def write(p,x):p.write_text(json.dumps(x,indent=2)+"\n")
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(1900000000,1900000000))
 resource.setrlimit(resource.RLIMIT_FSIZE,(33554432,33554432))
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--partition",default="train");ap.add_argument("--case",type=int,required=True)
 ap.add_argument("--sizes",default="16");ap.add_argument("--repetitions",type=int,default=1)
 ap.add_argument("--policies",default="trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope")
 ap.add_argument("--stage",default="expression_pilot");a=ap.parse_args()
 plan=json.load(open(HERE/"plan.json"));out=HERE/a.stage;out.mkdir(exist_ok=True)
 work=pathlib.Path(os.environ["KIRA_ACCEL_SCRATCH"]);policies=a.policies.split(",");trials=[]
 if a.policies=="expression_frozen":
  freeze=json.loads((HERE/"expression_freeze.json").read_text())
  for name,digest in freeze["sha256"].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
  policies=freeze["policies"]
 if a.policies=="frozen":
  frozen=json.loads((HERE/"frozen_policy.json").read_text())
  for name,digest in frozen["sha256"].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
  policies=frozen["policies"]
 if a.stage=="component_pilot" and "ml_components_lower" not in policies:policies.append("ml_components_lower")
 for size in map(int,a.sizes.split(",")):
  for rep in range(a.repetitions):
   r=(a.case+rep)%len(policies)
   for policy in policies[r:]+policies[:r]:trials.append((size,rep,policy))
 prefix="%s_%02d"%(a.partition,a.case)
 metadata_prefix=prefix+"_sizes"+a.sizes.replace(",","-")
 write(out/("environment_"+metadata_prefix+".json"),dict(host=platform.node(),
  cpu=next(x.split(":",1)[1].strip() for x in pathlib.Path("/proc/cpuinfo").read_text().splitlines() if x.startswith("model name")),
  plan_sha256=hashlib.sha256((HERE/"plan.json").read_bytes()).hexdigest()))
 for number,(size,rep,policy) in enumerate(trials):
  name="%s_n%d_r%d_%s"%(prefix,size,rep,policy);dest=out/(name+".json.gz")
  if dest.exists():continue
  if a.stage=="expression_test":
   earlier=[]
   for prior in sorted(out.glob("%s_n%d_r*_%s.json.gz"%(prefix,size,policy))):
    with gzip.open(prior,"rt") as stream:old=json.load(stream)
    if old.get("measured",True) and not old["success"]:earlier.append(prior.name)
   if earlier:
    skipped=dict(trial=name,partition=a.partition,case=a.case,size=size,repetition=rep,policy=policy,
     success=False,status="skipped_after_failure",measured=False,cold_seconds=None,trigger=earlier[0],
     reason="Do not repeat an identical bounded calculation after a failed attempt; retain the failed observation and mark all skipped repetitions explicitly.")
    with gzip.open(dest,"wt") as stream:json.dump(skipped,stream,separators=(",",":"))
    print(json.dumps(dict(trial=name,status=skipped["status"],trigger=earlier[0])),flush=True)
    continue
  total=allocated(HERE)
  if total>plan["retained_bytes_limit"] or plan["previous_project_upper_bytes"]+4*total+200000000>=10000000000:
   raise RuntimeError("Project storage headroom guard")
  if shutil.disk_usage(work).free<250000000:raise RuntimeError("Scratch headroom")
  scratch=work/name;scratch.mkdir();record=scratch/"record.json";peak=0;diskpeak=0;reason=None;t=time.perf_counter()
  with (scratch/"worker.log").open("w") as log:
   p=subprocess.Popen([str(ROOT/".tools/seed-model/venv/bin/python"),str(HERE/"s78_expression_controls_worker.py"),
    a.partition,str(a.case),str(size),policy,str(scratch),str(record)],stdout=log,stderr=subprocess.STDOUT,
    start_new_session=True,preexec_fn=limits)
   nextdisk=0.
   while p.poll() is None:
    elapsed=time.perf_counter()-t;peak=max(peak,rss_tree(p.pid))
    if elapsed>=nextdisk:diskpeak=max(diskpeak,allocated(scratch));nextdisk=elapsed+.5
    if elapsed>plan["timeout_seconds"]:reason="timeout"
    if peak>plan["rss_limit_bytes"]:reason="rss_limit"
    if diskpeak>plan["scratch_limit_bytes"]:reason="scratch_limit"
    if reason:
     os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=2)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
     break
    time.sleep(.05)
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  result=json.load(open(record)) if record.exists() else {"success":False}
  result.update(trial=name,partition=a.partition,case=a.case,size=size,repetition=rep,policy=policy,
   worker_sha256=hashlib.sha256((HERE/"s78_expression_controls_worker.py").read_bytes()).hexdigest(),cold_seconds=time.perf_counter()-t,peak_rss_bytes=peak,scratch_peak_bytes=diskpeak,returncode=p.returncode,
   status=reason or ("completed" if p.returncode==0 else "error"))
  evidence={}
  for path in scratch.rglob("*"):
   if path.is_file() and path.name in ["worker.log","run.log","jobs.yaml","integralfamilies.yaml","kinematics.yaml","kira_targets.kira","seed_audit.json","seeds.txt","context.json","forward.jsonl","row_trace.txt","cpp_choices.jsonl","cpp_context.txt"]:
    evidence[str(path.relative_to(scratch))]=path.read_text(errors="replace")
  for path in scratch.rglob("*.policy.jsonl.gz"):
   with gzip.open(path,"rt") as stream:evidence[str(path.relative_to(scratch))]=stream.read()
  result["evidence"]=pack(evidence)
  with gzip.open(dest,"wt",encoding="utf-8") as stream:json.dump(result,stream,separators=(",",":"),allow_nan=False)
  shutil.rmtree(scratch)
  write(out/("status_"+metadata_prefix+".json"),dict(completed=number+1,total=len(trials),last_trial=name,success=result["success"],status=result["status"]))
  print(json.dumps({k:result[k] for k in ["trial","cold_seconds","status","success"]}),flush=True)
 write(out/("complete_"+metadata_prefix+".json"),dict(trials=len(trials),completed=True))
if __name__=="__main__":main()
