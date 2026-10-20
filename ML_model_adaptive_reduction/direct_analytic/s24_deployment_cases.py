"""Fresh final requests after validation retains the preceding native model."""
from s00_direct_common import *
from s03_cases import cases as candidates
from s07_exact_cases import cases as exact_cases

def cases():
 # New whole target batches for every exact domain; no model is fitted to them.
 out=[]
 for c in exact_cases():
  cc=copy.deepcopy(c);cc['id']='final_'+c['id'];cc['targets']=[[a[0]+1]+a[1:] for a in c['targets']];cc['size']=len(cc['targets']);out.append(cc)
 blocked=set()
 sources=[load('direct_block_light',PRIOR/'s06_native_cases.py').native_cases,load('direct_block_vac',current().previous().previous().HERE/'s04_cases.py').native_cases]
 for gen in sources:
  for phase in ['training','validation','reserved']:blocked.update(tuple(sorted(map(tuple,c['targets']))) for c in gen(phase))
 for phase in ['development','training','validation','reserved']:blocked.update(tuple(sorted(map(tuple,c['targets']))) for c in candidates(phase))
 for name in ['protocol.json.gz','fast_protocol.json.gz']:
  for c in read(ROOT/'ML_model_adaptive_reduction/tensor_reduction'/name)['cases']:
   if c['test_group']=='native':blocked.add(tuple(sorted(map(tuple,c['targets']))))
 rng=random.Random(24439);powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4];pool=[]
 while len(pool)<8:
  n=rng.choice([2,3,4,5,6]);ts=tuple(sorted(tuple([1]*7+[-a,-b]) for a,b in rng.sample(powers,n)))
  if ts not in blocked and ts not in pool:pool.append(ts)
 h=helper()
 for kind in ['double_box','nonplanar_box']:
  for i,ts in enumerate(pool):
   c=h.inputs.case(kind,24443,'rank2','reserved');c.update(id=f'final_{kind}_{i}',targets=list(map(list,ts)),size=len(ts),test_group='native');out.append(current().previous().previous().batch.canonical(c))
 return out
