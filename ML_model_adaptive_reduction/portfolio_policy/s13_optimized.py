"""Combine frozen seed choices with exact bounded sector storage."""
from s00_common import *
from contextlib import contextmanager
BIN=ROOT/'.tools/kira-sector-storage/kira'
@contextmanager
def bounded(c):
 d=c['definition'];tops=d['top_level_sectors'];n=len(d['propagators'])
 admitted=(0<n<=31 and len(tops)==1 and tops[0]>0 and tops[0]&(tops[0]+1)==0 and not d.get('cut_propagators') and not d.get('symbolic_ibp'))
 policy=read(HERE/'integration/deployment.json')
 rule=next((r for r in policy['rules'] if r['signature']==inputs.signature(c)),None)
 admitted=admitted and rule is not None
 binary=ROOT/('.tools/kira-sector-wide/kira' if rule and rule['width']==128 else '.tools/kira-sector-storage/kira')
 state=dict(eligible=admitted,used=False,called=False,width=rule['width'] if admitted else 64)
 original=rt.native.run
 def run(*args,**kw):
  state['used']=rule['bounded'];state['called']=True
  old={k:os.environ.get(k) for k in ['KIRA_RUNTIME_BINARY','KIRA_BOUNDED_SECTOR_ARRAYS']}
  os.environ['KIRA_RUNTIME_BINARY']=str(binary)
  if rule['bounded']:os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  else:os.environ.pop('KIRA_BOUNDED_SECTOR_ARRAYS',None)
  try:return original(*args,**kw)
  finally:
   for k,v in old.items():
    if v is None:os.environ.pop(k,None)
    else:os.environ[k]=v
 if admitted:
  assert binary.exists();rt.native.run=run
 try:yield state
 finally:rt.native.run=original

def reduce(c,basis,method='application',reference=None):
 begin=time.perf_counter()
 with bounded(c) as active:
  if method=='application':
   deployment=read(HERE/'trained_model/deployment.json');pattern=module('portfolio_patterns',HERE/'s19_freeze_deployment.py').pattern(c)
   selected=any(v['signature']==inputs.signature(c) and v['pattern']==pattern for v in deployment['rules'])
   if selected:
    seed=module('portfolio_seed',HERE/'s01_application.py').reduce
    r=seed(c,basis,'learned',reference);r['route']='validated_target_pattern'
   else:
    application=module('portfolio_production',HERE/'s08_reduce.py').reduce
    r=application(c,basis,reference)
  else:
   seed=module('portfolio_seed',HERE/'s01_application.py').reduce
   r=seed(c,basis,method,reference)
 r.update(bounded_sector_storage=active['used'],integral_weight_bits=active['width'] if active['called'] else None,complete_seconds=time.perf_counter()-begin);return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--case');p.add_argument('--basis');p.add_argument('--output',required=True);a=p.parse_args();req=read(a.input) if a.input else dict(case=read(a.case),basis=read(a.basis),method='optimized_application');c=req['case'];m=req['method'];basis=req['basis'];ref=req.get('reference')
 try:
  if m.startswith('optimized_'):r=reduce(c,basis,m[len('optimized_'):],ref)
  elif m=='native':
   native=module('portfolio_seed',HERE/'s01_application.py').reduce
   r=native(c,basis,'native',ref)
  elif m=='previous':
   sys.path.insert(0,str(ROOT/'ML_model_seed_selection/joint_policy'));import s05_application
   r=s05_application.Reducer('learned',reuse=False).reduce({k:c[k] for k in ['id','size','definition','targets']},basis,ref)
  else:raise ValueError(m)
 except Exception as e:r=dict(success=False,error=str(e),traceback=traceback.format_exc()[-1500:])
 raw=gzip.compress(json.dumps(rt.compact(r)|dict(case=c['id'],method=m,worker=os.uname().nodename),separators=(',',':')).encode(),mtime=0);assert len(raw)<=1024**2
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_bytes(raw)
