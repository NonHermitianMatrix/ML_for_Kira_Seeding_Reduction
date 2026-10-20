"""Measure bounded fresh-process application costs, including model inference."""
from s00_tensor_common import *
import subprocess,signal,shutil

def measured(c,method,worker,limit=18):
 request=HERE/'requests'/f'case{worker}.json';output=(PRIOR if method=='previous' else HERE)/'requests'/f'tensor_result{worker}.json.gz'
 script=PRIOR/'s18_fast_runtime.py' if method=='previous' else HERE/'s02_runtime.py'
 write(request,c);output.unlink(missing_ok=True);start=time.perf_counter()
 proc=subprocess.Popen([sys.executable,str(script),'--case',str(request),'--output',str(output),'--method','integrated' if method=='previous' else method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=proc.communicate(timeout=limit);r=read(output) if output.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-500:]
 except subprocess.TimeoutExpired:
  h=previous().batch.legacy().h;helper=h.inputs.module('tensor_process_limits',h.BLOCK/'s11_extension_test.py');pids=helper.descendants(proc.pid)
  for pid in pids:
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  proc.communicate();r=dict(success=False,status='application_deadline')
  for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ['TMPDIR'])]:
   for pid in pids:
    for scratch in root.glob(f'ml_kira_{pid}_*'):
     if scratch.is_dir():shutil.rmtree(scratch)
 finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
 return r,time.perf_counter()-start
