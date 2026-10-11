"""Public interface for the validated arithmetic and compiled-reader extension."""
import argparse
import s14_reader as upgraded
from s00_backend import *
from s03_application import process
from s02_engine import MODES
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input");ap.add_argument("--output");ap.add_argument("--mode",choices=MODES+["deployed"],default="deployed");ap.add_argument("--policy",choices=POLICIES)
 ap.add_argument("--stream",action="store_true");ap.add_argument("--max-requests",type=int,default=64);a=ap.parse_args()
 assert os.environ.get("JOB_ID") and 1<=a.max_requests<=64
 dep=read(HERE/"reader_deployment.json") if a.mode=="deployed" else {};mode=dep.get("mode",a.mode);policy=a.policy or dep.get("policy");state={}
 if not a.stream:
  assert a.input and a.output;print(json.dumps(process(dict(input=a.input,output=a.output),mode,state,policy)),flush=True);return
 assert not a.input and not a.output;n=0
 while True:
  line=sys.stdin.buffer.readline(1048577)
  if not line:break
  if len(line)>1048576 or n>=a.max_requests:raise ValueError("Worker command limit")
  n+=1
  try:r=process(json.loads(line),mode,state,policy)
  except (AssertionError,ValueError,KeyError,RuntimeError,OSError) as e:r=dict(ok=False,error=str(e))
  print(json.dumps(r),flush=True)
if __name__=="__main__":main()
