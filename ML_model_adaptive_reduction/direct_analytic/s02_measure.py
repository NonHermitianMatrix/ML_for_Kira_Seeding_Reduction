"""Complete fresh-process cost, including bounded failed attempts."""
from s00_direct_common import *
import subprocess,signal,shutil

def measured(c,method,worker,limit=30):
 request=HERE/'requests'/f'case{worker}.json';out=HERE/'requests'/f'result{worker}.json.gz';write(request,c);out.unlink(missing_ok=True)
 start=time.perf_counter();p=subprocess.Popen([sys.executable,str(HERE/'s01_runtime.py'),'--case',str(request),'--output',str(out),'--method',method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=p.communicate(timeout=limit);r=read(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-600:]
 except subprocess.TimeoutExpired:
  h=helper();limits=h.inputs.module('direct_limits',h.BLOCK/'s11_extension_test.py');pids=limits.descendants(p.pid)
  for pid in pids:
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
  for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ.get('TMPDIR','/tmp'))]:
   for pid in pids:
    for q in root.glob(f'ml_kira_{pid}_*'):
     if q.is_dir():shutil.rmtree(q)
 finally:request.unlink(missing_ok=True);out.unlink(missing_ok=True)
 return r,time.perf_counter()-start
