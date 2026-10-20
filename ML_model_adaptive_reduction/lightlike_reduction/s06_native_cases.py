"""Fresh native patterns with disjoint training, validation, and reserved targets."""
from s00_light_common import *

def native_cases(phase):
 vac=previous().previous();h=vac.batch.legacy().h
 old=load('lightlike_old_native_cases',vac.HERE/'s04_cases.py');blocked=set()
 for p in ['training','validation','reserved']:
  blocked.update(tuple(sorted(tuple(t) for t in c['targets'])) for c in old.native_cases(p))
 # Also keep the last two frozen tensor-study native collections separate.
 for name in ['protocol.json.gz','fast_protocol.json.gz']:
  for c in read(PRIOR/name)['cases']:
   if c['test_group']=='native':blocked.add(tuple(sorted(tuple(t) for t in c['targets'])))
 rng=random.Random(19077);powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4];pool=[]
 while len(pool)<40:
  n=rng.choice([1,2,3,4,5,6]);ts=tuple(sorted(tuple([1]*7+[-a,-b]) for a,b in rng.sample(powers,n)))
  if ts not in blocked and ts not in pool:pool.append(ts)
 lo,hi,profile={'training':(0,16,19079),'validation':(16,24,19121),'reserved':(24,36,19139)}[phase];out=[]
 for kind in ['double_box','nonplanar_box']:
  for i in range(lo,hi):
   c=h.inputs.case(kind,profile,'rank2',phase);c.update(id=f'lightml_{phase}_{kind}_{i}',targets=[list(t) for t in pool[i]],size=len(pool[i]),test_group='native');out.append(vac.batch.canonical(c))
 if phase=='training':
  ts=tuple(sorted(tuple([1]*7+[0,-v]) for v in [2,3,4]));assert ts not in blocked and ts not in pool
  for kind in ['double_box','nonplanar_box']:
   c=h.inputs.case(kind,19083,'rank2',phase);c.update(id=f'lightml_training_{kind}_boundary',targets=[list(t) for t in ts],size=len(ts),test_group='native');out.append(vac.batch.canonical(c))
 return out
