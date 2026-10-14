"""Serve consecutive reduction requests with models loaded once in a dedicated worker."""
import json,sys,time
from pathlib import Path
import s06_test as test
w=test.w
class Session:
 """A sequential session; each request starts fresh exact Kira attempts."""
 def __init__(self):
  self.frozen=json.loads((w.HERE/'trained_model/freeze.json').read_text())
  test.model.check_freeze(self.frozen)
 def reduce(self,case,basis):
  begin=time.perf_counter()
  assert 0<case['size']==len(case['targets'])<=128
  result=test.application(case,basis,self.frozen)
  result.update(application_seconds=time.perf_counter()-begin,reused_loaded_model=True)
  return result

def main():
 session=Session();count=0;input_bytes=0;output_bytes=0
 while True:
  line=sys.stdin.buffer.readline(1024**2+1)
  if not line:break
  assert len(line)<=1024**2 and line.endswith(b'\n')
  input_bytes+=len(line);count+=1
  assert input_bytes<=4*1024**2 and count<=128
  request=json.loads(line);case=request['case']
  result=session.reduce(case,request['basis'])
  data=json.dumps(dict(case=case['id'],result=result),separators=(',',':'))
  size=len(data.encode())+1;output_bytes+=size
  assert size<=1024**2 and output_bytes<=16*1024**2
  print(data,flush=True)
  if not result['success']:raise SystemExit(2)
if __name__=='__main__':main()
