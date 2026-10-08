"""Run counterbalanced matched trials with bounded processes and archived evidence."""
import argparse,gzip,json,os,pathlib,resource,shutil,signal,subprocess,sys,time,platform
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2)+"\n")
def allocated(p):
 total=0
 for base,dirs,files in os.walk(p):
  for name in files:
   try:total+=os.stat(os.path.join(base,name),follow_symlinks=False).st_blocks*512
   except FileNotFoundError:pass
 return total
def rss_tree(pid):
 pending=[pid];seen=set();rss=0
 while pending:
  p=pending.pop()
  if p in seen:continue
  seen.add(p)
  try:
   rss+=int(pathlib.Path("/proc/%d/statm"%p).read_text().split()[1])*os.sysconf("SC_PAGE_SIZE")
   pending+=list(map(int,pathlib.Path("/proc/%d/task/%d/children"%(p,p)).read_text().split()))
  except (FileNotFoundError,ProcessLookupError,IndexError):pass
 return rss
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(1610612736,1610612736))
 resource.setrlimit(resource.RLIMIT_FSIZE,(16777216,16777216))
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--pilot",action="store_true");args=ap.parse_args()
 plan=read(HERE/"plan.json");out=HERE/("pilot" if args.pilot else "results");out.mkdir(exist_ok=True)
 work=pathlib.Path(os.environ["KIRA_COMPARISON_SCRATCH"]);work.mkdir(exist_ok=True)
 python=ROOT/".tools/seed-model/venv/bin/python"
 cases=[]
 for i,c in enumerate(plan["family_cases"]):
  sizes=sorted(set(min(s,c["meta"]["counts"]["targets"]) for s in plan["batch_sizes"]))
  policies=plan["policies"]+(plan["native_policies"] if c["domain"]!="vacuum" else [])
  if args.pilot:
   if c["domain"] not in ["tadpole","bubble","propagator"] and not (c["domain"]=="vacuum" and c["meta"]["loops"]==2):continue
   sizes=[1]
  for size in sizes:
   for rep in range(1 if args.pilot else plan["repetitions"]):
    rotation=(i+rep)%len(policies)
    for policy in policies[rotation:]+policies[:rotation]:cases.append((i,size,rep,policy))
 meta=dict(host=platform.node(),platform=platform.platform(),cpu=next((x.split(":",1)[1].strip() for x in pathlib.Path("/proc/cpuinfo").read_text().splitlines() if x.startswith("model name")),None),
   processes="one trial at a time; one Kira and one Torch thread",plan=plan,total_trials=len(cases))
 write(out/"environment.json",meta)
 for number,(i,size,rep,policy) in enumerate(cases):
  name="%02d_n%02d_r%d_%s"%(i,size,rep,policy);dest=out/(name+".json.gz")
  if dest.exists():continue
  if allocated(HERE)>plan["result_limit"]:raise RuntimeError("Published comparison output limit")
  if shutil.disk_usage(work).free<200000000:raise RuntimeError("Filesystem headroom")
  scratch=work/name;scratch.mkdir();record=scratch/"record.json";reason=None;peak=0;scratchpeak=0
  start=time.perf_counter()
  with (scratch/"worker.log").open("w") as log:
   proc=subprocess.Popen([str(python),str(HERE/"s02_worker.py"),str(i),str(size),policy,str(scratch),str(record)],
      stdout=log,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits)
   nextdisk=0
   while proc.poll() is None:
    elapsed=time.perf_counter()-start;peak=max(peak,rss_tree(proc.pid))
    if elapsed>=nextdisk:
     scratchpeak=max(scratchpeak,allocated(scratch));nextdisk=elapsed+.5
    if elapsed>plan["timeout_seconds"]:reason="timeout"
    if scratchpeak>plan["case_scratch_limit"]:reason="scratch_limit"
    if peak>1400000000:reason="rss_limit"
    if reason:
     os.killpg(proc.pid,signal.SIGTERM)
     try:proc.wait(timeout=2)
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
     break
    time.sleep(.05)
  cold=time.perf_counter()-start
  result=read(record) if record.exists() else dict(success=False)
  result.update(case=i,size=size,repetition=rep,policy=policy,trial=name,cold_seconds=cold,
   process_tree_peak_rss_bytes=peak,scratch_peak_bytes=scratchpeak,returncode=proc.returncode,
   resource_status=reason or ("completed" if proc.returncode==0 else "error"))
  evidence={}
  for p in scratch.rglob("*"):
   if not p.is_file():continue
   relative=str(p.relative_to(scratch))
   if p.name in ["run.log","worker.log","jobs.yaml","integralfamilies.yaml","kinematics.yaml"] or p.name=="kira_targets.kira":
    if p.stat().st_size<=2097152:evidence[relative]=p.read_text(errors="replace")
    else:evidence[relative]=p.read_text(errors="replace")[-65536:]
  result["evidence"]=evidence
  with gzip.open(dest,"wt") as f:json.dump(result,f,separators=(",",":"),allow_nan=False)
  shutil.rmtree(scratch)
  write(out/"status.json",dict(completed=number+1,total=len(cases),latest=name,resource_status=result["resource_status"],success=result["success"]))
  print(json.dumps(dict(completed=number+1,total=len(cases),trial=name,status=result["resource_status"],success=result["success"],seconds=cold)),flush=True)
 write(out/"complete.json",dict(trials=len(cases),completed=True))
if __name__=="__main__":main()
