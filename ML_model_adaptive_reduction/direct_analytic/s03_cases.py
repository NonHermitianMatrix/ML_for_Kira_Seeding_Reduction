"""Separate development, training, validation, and reserved native targets."""
from s00_direct_common import *

def cases(phase):
 old=current();h=helper();maker=load('direct_old_cases',PRIOR/'s06_native_cases.py');blocked=set()
 for p in ['training','validation','reserved']:
  blocked.update(tuple(sorted(tuple(t) for t in c['targets'])) for c in maker.native_cases(p))
 older=load('direct_older_cases',old.previous().previous().HERE/'s04_cases.py')
 for p in ['training','validation','reserved']:
  blocked.update(tuple(sorted(tuple(t) for t in c['targets'])) for c in older.native_cases(p))
 for name in ['protocol.json.gz','fast_protocol.json.gz']:
  for c in read(ROOT/'ML_model_adaptive_reduction/tensor_reduction'/name)['cases']:
   if c['test_group']=='native':blocked.add(tuple(sorted(tuple(t) for t in c['targets'])))
 rng=random.Random(22303);powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4];pool=[]
 while len(pool)<30:
  n=rng.choice([2,3,4,5,6]);ts=tuple(sorted(tuple([1]*7+[-a,-b]) for a,b in rng.sample(powers,n)))
  if ts not in blocked and ts not in pool:pool.append(ts)
 lo,hi,profile={'development':(0,2,22307),'training':(2,14,22343),'validation':(14,20,22349),'reserved':(20,28,22367)}[phase];out=[]
 for kind in ['double_box','nonplanar_box']:
  for i in range(lo,hi):
   c=h.inputs.case(kind,profile,'rank2',phase);c.update(id=f'direct_{phase}_{kind}_{i}',targets=[list(t) for t in pool[i]],size=len(pool[i]),test_group='native');out.append(old.previous().previous().batch.canonical(c))
 return out
