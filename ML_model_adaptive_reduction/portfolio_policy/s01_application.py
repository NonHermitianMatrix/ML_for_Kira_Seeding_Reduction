"""Apply a family-aware cost model before native IBP equation generation."""
from s00_common import *

def predict(m,x):
 import struct
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x];out=[0.]*len(ACTIONS)
 for t in m['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  for j,v in enumerate(t['value'][i]):out[j]+=v/len(m['trees'])
 return out

def reduce(c,basis,method='learned',reference=None):
 start=time.perf_counter();scores=None;selected='native';reason='native_control'
 if method in ['learned','fixed']:
  cfg=read(HERE/'trained_model/fixed.json');g=inputs.signature(c);entry=cfg['domains'].get(g)
  if entry:
   x=features(c);guard=all(entry['minimum'][i]-1e-9<=x[i]<=entry['maximum'][i]+1e-9 for i in [4,5,6,7,21,25])
   if guard:
    selected=entry['action'];reason='fixed_validated'
    if method=='learned' and entry['enabled']:
     f=read(HERE/'trained_model'/entry['model_file']);scores=predict(f['model'],x)
     k=min(range(len(ACTIONS)),key=scores.__getitem__);b=ACTIONS.index(selected)
     if scores[k]<scores[b]-entry['margin']:selected=ACTIONS[k]
     reason='learned_cost'
   else:reason='outside_feature_domain'
  else:reason='unknown_family'
 decision=time.perf_counter()-start
 r=rt.run(c,basis,'native',reference,first=selected,timeout=60)
 r.update(method=method,selection=dict(action=selected,prediction_used=scores is not None,scores=scores,reason=reason,seconds=decision),complete_seconds=time.perf_counter()-start)
 return r

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();req=read(a.input)
 c=req['case'];basis=req.get('basis');ref=req.get('reference');method=req['method']
 try:
  if method in ['reference','check']:
   b=inputs.bounds(c,'expanded')
   if method=='check':b[1]+=1
   with rt.environment():r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=90,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=2 if method=='check' else 1,threads=1)
   if ref:rt.verify(r,ref)
  elif method.startswith('action_'):r=rt.run(c,basis,'native',ref,first=method[7:],timeout=60)
  elif method=='production':
   production=module('portfolio_production',HERE/'s08_reduce.py').reduce
   r=production(c,basis,ref)
  elif method=='previous':
   sys.path.insert(0,str(ROOT/'ML_model_seed_selection/joint_policy'))
   import s05_application as previous
   r=previous.Reducer('learned',reuse=False).reduce({k:c[k] for k in ['id','size','definition','targets']},basis,ref)
  else:r=reduce(c,basis,method,ref)
 except Exception as e:
  import traceback
  r=dict(success=False,status='exception',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc()[-1500:])
 r=rt.compact(r);r.update(case=c['id'],method=method,worker=os.uname().nodename)
 if c['split']=='reserved' and method in ['native','fixed','learned','previous','production']:
  # The parent checks the study reserve before timing. Keep the whole-study
  # administrative scan out of the production request for every control.
  raw=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
  assert len(raw)<=1024**2
  Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_bytes(raw)
 else:write(a.output,r)
