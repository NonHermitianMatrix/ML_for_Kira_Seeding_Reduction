"""Bound the complete process, including model loading and exact verification."""
import shutil,json,os,pathlib,resource,signal,subprocess,sys,time
from s02_run import process_rss
from s04_records import read_record,write_record
HERE=pathlib.Path(__file__).resolve().parent
def descendants(pid):
 todo=[pid];seen=set()
 while todo:
  v=todo.pop()
  if v in seen:continue
  seen.add(v)
  try:
   for t in (pathlib.Path("/proc")/str(v)/"task").iterdir():
    try:todo.extend(map(int,(t/"children").read_text().split()))
    except (ValueError,OSError):pass
  except OSError:pass
 return seen
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2800*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def execute_fresh(case,size,policy,output,reference,timeout=360,trace=False):
 output=pathlib.Path(output)
 if output.exists():return read_record(output)
 begin=time.perf_counter()
 cmd=[sys.executable,str(HERE/"s14_worker.py"),case["id"],str(size),policy,str(output),str(reference),"--timeout",str(timeout)]
 if trace:cmd+=["--trace"]
 env=dict(os.environ,KIRA_WORKFLOW_START=str(begin))
 # The worker prints only one short status record; pipes stay far below capacity.
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,start_new_session=True,preexec_fn=limits)
 reason=None;peak=0
 while proc.poll() is None:
  peak=max(peak,process_rss(proc.pid))
  if time.perf_counter()-begin>timeout+15:reason="workflow_time_limit"
  if peak>2600*1024**2:reason="workflow_memory_limit"
  if reason:
   for pid in sorted(descendants(proc.pid),reverse=True):
    try:os.kill(pid,signal.SIGKILL)
    except ProcessLookupError:pass
   break
  time.sleep(.2)
 stdout,stderr=proc.communicate()
 for scratch in (HERE.parents[1]/".tools/kira-cost-training").glob(f"run_{proc.pid}_*"):
  shutil.rmtree(scratch)
 if output.exists():
  r=read_record(output)
 else:
  r=dict(case=case["id"],group=case["group"],topology=case["topology_group"],split=case["split"],
   loops=len(case["definition"]["loop_momenta"]),size=size,policy=policy,success=False,
   completed_targets=0,incomplete_targets=size,complete_seconds=time.perf_counter()-begin,
   timeout_seconds=timeout,fallback_attempts=0,attempts=[],status=reason or "worker_failed",
   error=stderr[-4000:],returncode=proc.returncode)
  write_record(output,r)
 monitor=output.with_name(output.name.replace(".json.gz","_monitor.json.gz"))
 if not monitor.exists():write_record(monitor,dict(case=case["id"],policy=policy,peak_tree_rss_bytes=peak,
   enclosing_seconds=time.perf_counter()-begin,returncode=proc.returncode,reason=reason,stderr=stderr[-2000:]))
 return r
