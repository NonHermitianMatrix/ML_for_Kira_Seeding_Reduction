"""Bounded single-batch and persistent interfaces with lossless coefficient output."""
import argparse
from s02_engine import *
def process(cmd,mode,state,forced_policy=None):
 t=time.perf_counter();inp=Path(cmd["input"]).resolve();dest=Path(cmd["output"]).resolve()
 assert ROOT in inp.parents and HERE in dest.parents
 assert inp.stat().st_size<=1024*1024
 requests=read(inp)["requests"];result=apply(requests,mode,state,forced_policy)
 result.update(complete_seconds=time.perf_counter()-t,request_sha256=sha(inp),worker_pid=os.getpid())
 r=save(dest,result);guard()
 return dict(ok=r["success"],output=str(dest.relative_to(HERE)),fallbacks=r["fallbacks"])
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input");ap.add_argument("--output");ap.add_argument("--mode",default="deployed",choices=MODES+["deployed"]);ap.add_argument("--policy",choices=POLICIES)
 ap.add_argument("--stream",action="store_true");ap.add_argument("--max-requests",type=int,default=64);a=ap.parse_args()
 assert os.environ.get("JOB_ID") and 1<=a.max_requests<=64,"Use a bounded scheduler allocation"
 dep=read(HERE/"deployment.json") if a.mode=="deployed" else {};mode=dep.get("mode",a.mode);state={}
 if not a.policy and a.mode=="deployed":a.policy=dep.get("policy")
 if not a.stream:
  assert a.input and a.output;print(json.dumps(process(dict(input=a.input,output=a.output),mode,state,a.policy)),flush=True);return
 assert not a.input and not a.output;n=0
 while True:
  line=sys.stdin.buffer.readline(1048577)
  if not line:break
  if len(line)>1048576 or n>=a.max_requests:raise ValueError("Worker command limit")
  n+=1
  try:r=process(json.loads(line),mode,state,a.policy)
  except (AssertionError,ValueError,KeyError,RuntimeError,OSError) as e:r=dict(ok=False,error=str(e))
  print(json.dumps(r),flush=True)
if __name__=="__main__":main()
