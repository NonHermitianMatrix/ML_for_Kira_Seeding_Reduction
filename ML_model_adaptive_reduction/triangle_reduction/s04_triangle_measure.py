"""Complete fresh-process time, bounded execution, and exact comparison."""
from s00_triangle_common import *
import signal,shutil

def measured(c,action,worker,limit=90):
 request=HERE/'requests'/f'input{worker}.json';out=HERE/'requests'/f'output{worker}.json.gz';write(request,c);out.unlink(missing_ok=True)
 start=time.perf_counter();p=subprocess.Popen([sys.executable,str(HERE/'s03_triangle_runtime.py'),'--case',str(request),'--output',str(out),'--action',action],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
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

def triangle_rows(c,r):
 import sympy as sp
 recognize=load("triangle_exact_check",HERE/"s01_triangle.py").recognize
 d=sp.Symbol('d');out={}
 for t in c['targets']:
  total=sp.S.One;covered=set()
  for b in r['blocks']:
   ids=b['indices'];covered.update(ids);row=b['result']['coefficients'][label([t[i] for i in ids])];part=sp.S.Zero
   groups=recognize(b['case']);assert groups is not None
   for key,value in row.items():
    m=list(map(int,key.split(',')));factor=sp.S.One;used=set()
    for a,v,z,q in groups:
     powers=[m[a],m[v],m[z]];assert powers in [[1,1,1],[1,0,1]],powers
     if powers==[1,1,1]:factor*=2*(d-3)/(sp.Rational(q.numerator,q.denominator)*(d-4))
     used.update([a,v,z])
    assert all(not v for i,v in enumerate(m) if i not in used)
    part+=sp.sympify(value.replace('^','**'),rational=True)*factor
   total*=part
  assert all(not v for i,v in enumerate(t) if i not in covered)
  out[label(t)]=total
 return out

def compare(c,r,ref):
 if not r.get('success') or not ref.get('success'):return False,0
 if c.get('test_group')=='triangle':
  import sympy as sp
  left=triangle_rows(c,r);right=triangle_rows(c,ref)
  return set(left)==set(right) and all(sp.cancel(left[k]-right[k])==0 for k in left),len(left)
 h=helper()
 if c.get('test_group') not in ['lightlike','ordinary_tensor']:return h.compare(r,ref)
 import sympy as sp
 def canonical(case,rows):
  masses=[sp.sympify(p['mass_squared']) for p in case['definition']['propagators']];out={}
  for target,row in rows.items():
   rr={}
   for master,value in row.items():
    a=list(map(int,master.split(',')))
    if sum(a)==1 and a.count(1)==1:
     mass=masses[a.index(1)]
     if mass==0:continue
     z=[0]*len(a);z[next(i for i,x in enumerate(masses) if sp.cancel(x-mass)==0)]=1;master=label(z)
    rr[master]=rr.get(master,0)+sp.sympify(value)
   out[target]={m:str(sp.cancel(v)) for m,v in rr.items() if sp.cancel(v)!=0}
  return out
 refs={tuple(b['indices']):b for b in ref['blocks']};n=0
 if len(r.get('blocks',[]))!=len(refs):return False,0
 for block in r['blocks']:
  other=refs.get(tuple(block['indices']))
  if other is None:return False,n
  ok,k=h.equal(canonical(block['case'],block['result']['coefficients']),canonical(other['case'],other['result']['coefficients']))
  if not ok:return False,n
  n+=k
 return True,n
