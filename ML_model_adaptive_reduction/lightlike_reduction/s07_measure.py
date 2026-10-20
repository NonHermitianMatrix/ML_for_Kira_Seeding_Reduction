"""Bounded complete-process measurements, including failed attempts."""
from s00_light_common import *
import subprocess,signal,shutil

def measured(c,method,worker,limit=20):
 request=HERE/'requests'/f'case{worker}.json';out=(PRIOR if method=='previous' else HERE)/'requests'/f'lightlike_result{worker}.json.gz';write(request,c);out.unlink(missing_ok=True)
 script=PRIOR/'s18_fast_runtime.py' if method=='previous' else HERE/'s05_runtime.py';start=time.perf_counter();p=subprocess.Popen([sys.executable,str(script),'--case',str(request),'--output',str(out),'--method','integrated' if method=='previous' else method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=p.communicate(timeout=limit);r=read(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-600:]
 except subprocess.TimeoutExpired:
  h=previous().previous().batch.legacy().h;helper=h.inputs.module('lightlike_process_limits',h.BLOCK/'s11_extension_test.py');pids=helper.descendants(p.pid)
  for pid in pids:
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
  for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ['TMPDIR'])]:
   for pid in pids:
    for q in root.glob(f'ml_kira_{pid}_*'):
     if q.is_dir():shutil.rmtree(q)
 finally:request.unlink(missing_ok=True);out.unlink(missing_ok=True)
 return r,time.perf_counter()-start
