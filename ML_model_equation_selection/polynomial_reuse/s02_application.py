"""Single-request and bounded persistent-worker interfaces."""
import argparse,os
from s01_engine import *
MAX_LINE=1024*1024
def process(command,variant,policy,state):
 start=time.perf_counter();inp=Path(command["input"]).resolve();out=Path(command["output"]).resolve()
 assert ROOT in inp.parents and HERE in out.parents,"Input and output must remain in their project domains"
 assert inp.stat().st_size<=MAX_LINE,"Input size limit"
 source=json.loads(inp.read_text());result=apply(source["requests"],variant,policy,state)
 result.update(complete_seconds=time.perf_counter()-start,request_sha256=base.sha(inp),worker_pid=os.getpid())
 stored=save(out,result)
 return dict(ok=True,output=str(out.relative_to(HERE)),success=stored["success"],complete_seconds=stored["complete_seconds"],fallbacks=stored["fallbacks"])
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path);ap.add_argument("--output",type=Path)
 ap.add_argument("--variant",choices=["deployed","baseline","transforms","taylor","both"],default="deployed")
 ap.add_argument("--policy",choices=["extreme","model"],default="extreme");ap.add_argument("--stream",action="store_true")
 ap.add_argument("--max-requests",type=int,default=64);a=ap.parse_args()
 assert os.environ.get("JOB_ID"),"Use a bounded scheduler job";assert 1<=a.max_requests<=64
 variant=json.loads((HERE/"deployment.json").read_text())["variant"] if a.variant=="deployed" else a.variant
 state=State()
 if not a.stream:
  assert a.input and a.output
  print(json.dumps(process(dict(input=str(a.input),output=str(a.output)),variant,a.policy,state)),flush=True);return
 assert a.input is None and a.output is None
 count=0
 while True:
  line=sys.stdin.buffer.readline(MAX_LINE+1)
  if not line:break
  if len(line)>MAX_LINE:raise ValueError("Worker command exceeds the size limit")
  if count>=a.max_requests:raise ValueError("Worker request limit reached")
  count+=1
  try:answer=process(json.loads(line),variant,a.policy,state)
  except (AssertionError,ValueError,KeyError,RuntimeError,OSError) as exc:answer=dict(ok=False,error=type(exc).__name__+": "+str(exc))
  print(json.dumps(answer),flush=True)
if __name__=="__main__":main()
