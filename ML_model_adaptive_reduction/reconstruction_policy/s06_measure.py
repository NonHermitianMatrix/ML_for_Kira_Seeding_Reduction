"""Measure complete applications and retain failed attempts."""
from s00_reconstruction_common import *
import signal,shutil

def measured(c,method,worker,limit=50,bunch=1,entry='s05_runtime.py'):
 assert entry in ['s05_runtime.py','s15_deploy.py']
 request=HERE/'requests'/f'case{worker}.json';out=HERE/'requests'/f'result{worker}.json.gz'
 write(request,c);out.unlink(missing_ok=True)
 start=time.perf_counter()
 command=[sys.executable,str(HERE/entry),'--case',str(request),'--output',str(out),'--method',method]
 if entry=='s05_runtime.py':command+=['--bunch',str(bunch)]
 p=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=p.communicate(timeout=limit)
  r=read(out) if out.exists() else dict(success=False,status='missing_output')
  r['stderr_tail']=err.decode(errors='replace')[-1200:]
 except subprocess.TimeoutExpired:
  h=helper();limits=h.inputs.module('reconstruction_limits',h.BLOCK/'s11_extension_test.py');pids=limits.descendants(p.pid)
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
