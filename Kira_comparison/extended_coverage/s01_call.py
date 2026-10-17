"""Run one bounded cold application or reference calculation."""
import argparse,os,sys,time,traceback
from s00_protocol import HERE,ROOT,read,write
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
tick=time.perf_counter();request=read(a.input)
sys.path.insert(0,str(ROOT/'ML_model_seed_selection/joint_policy'))
import s00_engine as engine
import s05_application as app
rt=engine.rt
original=rt.native.run
def bounded(*args,**kw):
 kw['timeout']=min(30,kw.get('timeout',30));kw['scratch_cap']=min(32*1024**2,kw.get('scratch_cap') or 32*1024**2)
 return original(*args,**kw)
rt.native.run=bounded
try:
 c=request['case'];basis=request.get('basis');ref=request.get('reference');method=request['method']
 minimal={k:c[k] for k in ['id','size','definition','targets']}
 sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/batch_policy'))
 from s16_deployment import normalize
 c=normalize(minimal)
 if method in ['reference','check']:
  b=list(engine.inputs.bounds(c,'expanded'))
  if method=='check':b[1]+=1
  with rt.environment():r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=30,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=2 if method=='check' else 1,threads=1)
  if ref:rt.verify(r,ref)
 elif method=='direct_exact':
  sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/massless_banana'));import s00_formula
  r=s00_formula.reduce(c,basis)
  if r is None:raise ValueError('Outside exact banana domain')
  if ref:rt.verify(r,ref)
 elif request.get('sequence'):
  reducer=app.Reducer('learned' if method.startswith('selected') else method,reuse=method=='selected_reuse');out=[]
  for item in request['sequence']:
   r0=reducer.reduce(item['case'],item['basis'],item['reference']);out.append(rt.compact(r0))
  r=dict(success=all(x['success'] for x in out),results=out,reference_checked=all(x['reference_checked'] for x in out),cache_hits=sum(x.get('route')=='exact_scale_reuse' for x in out))
 else:
  reducer=app.Reducer('learned' if method=='selected' else method,reuse=False)
  r=reducer.reduce(c,basis,ref)
except Exception as e:
 r=dict(success=False,status='exception',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc()[-2200:])
r=rt.compact(r);r.update(method=request['method'],case=request['case']['id'],worker=os.uname().nodename,process_internal_seconds=time.perf_counter()-tick)
write(a.output,r)
