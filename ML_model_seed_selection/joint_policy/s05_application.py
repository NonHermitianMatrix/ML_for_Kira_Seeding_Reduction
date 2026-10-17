"""Use frozen joint choices and optional exact scale reuse in one application."""
import argparse
from s00_engine import *
from s04_reuse import ScaleCache

def policy(c,method):
 if method=='native':return 'native',dict(prediction_used=False)
 prefix='fixed_' if method=='fixed' else ''
 for p in sorted((HERE/'trained_model').glob(prefix+'*.json')):
  if p.name.endswith('_freeze.json') or (method!='fixed' and p.name.startswith('fixed_')):continue
  f=rt.read(p)
  if inputs.signature(c)!=f['signature']:continue
  physical=c['definition']['physical_propagators'];rank=max(sum(max(0,-v) for v in t) for t in c['targets'])
  valid=len(c['targets'])==1 and all(t[:physical]==[1]*physical and all(v<=0 for v in t[physical:]) for t in c['targets']) and f['minimum_rank']<=rank<=f['maximum_rank']
  if not valid:return 'previous',dict(prediction_used=False,reason='outside_domain')
  if method=='learned' and not f['deploy']:return 'previous',dict(prediction_used=False,reason='validation_retained_previous')
  j=f['fixed_index'];scores=None
  if method=='learned' and f['enabled']:
   scores=previous.predict(f['model'],previous.feature(c));best=min(range(len(scores)),key=scores.__getitem__)
   if scores[best]<scores[j]-f['margin']:j=best
  return f['actions'][j],dict(prediction_used=scores is not None,index=j,scores=scores)
 return 'previous',dict(prediction_used=False,reason='unknown_family')

class Reducer:
 def __init__(self,method='learned',reuse=True):
  assert method in ['learned','fixed','native','previous']
  self.method=method;self.cache=ScaleCache() if reuse else None

 def reduce(self,c,basis,reference=None):
  start=time.perf_counter()
  sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/batch_policy'))
  from s16_deployment import normalize,validate
  c=normalize(c);validate(c,basis)
  identity=None
  if self.cache is not None:
   signatures=[rt.read(p)['signature'] for p in (HERE/'trained_model').glob('fixed_*.json')]
   identity=self.cache.identify(c,basis,signatures);r=self.cache.get(identity)
   if r is not None:
    r.update(case=c['id'],selection=dict(prediction_used=False),method=self.method)
    if reference:rt.verify(r,reference)
    r['complete_seconds']=time.perf_counter()-start;return r
  if self.method=='previous':name='previous';info=dict(prediction_used=False)
  else:name,info=policy(c,self.method)
  if name=='previous':
   from s11_integrated import reduce as old_app
   r=old_app(c,basis)
   if reference:rt.verify(r,reference)
  else:r=run(c,basis,name,reference)
  r.update(selection=info,method=self.method,route=r.get('route','joint_seed_and_order'))
  if self.cache is not None:self.cache.put(identity,r)
  r['complete_seconds']=time.perf_counter()-start;return r

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--case');ap.add_argument('--basis');ap.add_argument('--requests');ap.add_argument('--output',required=True);ap.add_argument('--method',choices=['learned','fixed','native','previous'],default='learned');ap.add_argument('--no-reuse',action='store_true');a=ap.parse_args()
 reducer=Reducer(a.method,not a.no_reuse)
 if a.requests:
  requests=rt.read(a.requests);results=[reducer.reduce(x['case'],x['basis']) for x in requests];r=dict(success=all(x['success'] for x in results),results=results,complete_seconds=sum(x['complete_seconds'] for x in results))
 else:
  if not a.case or not a.basis:ap.error('Supply --case and --basis, or --requests.')
  r=reducer.reduce(rt.read(a.case),rt.read(a.basis))
 save(a.output,r);print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'])))
