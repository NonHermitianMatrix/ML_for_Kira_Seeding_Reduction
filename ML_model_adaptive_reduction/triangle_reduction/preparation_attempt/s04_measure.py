"""Complete fresh-process time, bounded execution, and exact comparison."""
from s00_triangle_common import *
import signal,shutil

def measured(c,action,worker,limit=90):
 request=HERE/'requests'/f'input{worker}.json';out=HERE/'requests'/f'output{worker}.json.gz';write(request,c);out.unlink(missing_ok=True)
 start=time.perf_counter();p=subprocess.Popen([sys.executable,str(HERE/'s03_runtime.py'),'--case',str(request),'--output',str(out),'--action',action],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=p.communicate(timeout=limit);r=read(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-1200:]
 except subprocess.TimeoutExpired:
  h=helper();lim=h.inputs.module('triangle_limits',h.BLOCK/'s11_extension_test.py');pids=lim.descendants(p.pid)
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
 request.unlink(missing_ok=True);out.unlink(missing_ok=True)
 return r,time.perf_counter()-start

def native_triangle(c):
 h=helper()
 with h.rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  r=h.rt.compact(h.rt.native.run(c,c['size'],'native',HERE/'unused',timeout=40,margin=1,archive=False,records=False,scratch_cap=32*1024**2,ordering=1,threads=1))
 return dict(success=r['success'],blocks=[dict(case=c,indices=list(range(len(c['definition']['propagators']))),result=r)])

def compare(c,r,ref):
 prior().previous();helper();m=load('triangle_compare',prior().PREVIOUS/'s27_deploy_test.py');return m.compare(c,r,ref)
