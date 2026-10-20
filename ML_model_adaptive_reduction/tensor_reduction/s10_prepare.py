"""Freeze the model, inputs, and comparison rules before reserved measurements."""
from s00_tensor_common import *
from s03_cases import case,cases

def main():
 from s08_train import main as train
 from s09_checks import main as check
 train();check();old=previous();h=old.batch.legacy().h;families=h.inputs.module('tensor_product_families',h.BLOCK/'s01_families.py')
 tests=[dict(c,test_group='tensor') for c in cases('reserved')]
 for P,e,mass in [(2,1,'massless'),(2,2,'mixed'),(3,1,'mixed'),(4,1,'mixed')]:
  c=case(P,e,7589+P+e,rank=2,dots=1,count=2,mass=mass,seed=71);c['test_group']='other_masses';tests.append(c)
 for L in range(2,14):
  blocks=[case(2,1,7603+L,rank=2,dots=1,count=2,seed=83) for _ in range(L)]
  c=families.compose(blocks,'tensor_product_L'+str(L),'reserved');c['test_group']='products';tests.append(c)
 # Keep the preceding seed model fixed, and test unused numerator batches.
 rng=random.Random(6101);pool=[];powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4]
 while len(pool)<48:
  n=rng.choice([1,2,2,3,4]);v=tuple(sorted(rng.sample(powers,n)))
  if v not in pool:pool.append(v)
 for kind in ['double_box','nonplanar_box']:
  for i in range(44,48):
   c=h.inputs.case(kind,7649,'rank2','reserved_tensor');ts=[[1]*7+[-a,-b] for a,b in pool[i]]
   c.update(id=f'tensor_native_{kind}_p{i}',targets=ts,size=len(ts),test_group='native',scope='native_batch');tests.append(old.batch.canonical(c))
 for L in [1,3,7,13]:
  maker=load('tensor_vacuum_regression',PRIOR/'s04_cases.py');c=maker.vacuum_case(L,'chain',7681);c['test_group']='previous_exact';tests.append(c)
 # Every whole family profile is separate across new fitting and test sets.
 ids=[json.dumps([c['definition'],c['targets']],sort_keys=True) for phase in ['training','validation'] for c in cases(phase)]+[json.dumps([c['definition'],c['targets']],sort_keys=True) for c in tests]
 assert len(ids)==len(set(ids))
 write(HERE/'protocol.json.gz',dict(complete=True,repetitions=3,seconds_per_application=18,cases=tests,
 source_sha256={p.name:sha(p) for p in HERE.glob('s*.py') if int(p.name[1:3])<=12},model_sha256=sha(HERE/'trained_model/policy.json'),fixed_sha256=sha(HERE/'trained_model/fixed.json'),prior_model_sha256=sha(PRIOR/'trained_model/policy.json'),prior_entry_sha256=sha(PRIOR/'s18_fast_runtime.py'),
 objective='Complete fresh-process time. External coefficient comparisons are outside both application timers. Preserve every failure; ratios use only requests completed in all three repetitions by both methods.'))
 print(json.dumps(dict(frozen=True,requests=len(tests),model_enabled=read(HERE/'trained_model/policy.json')['enabled'])),flush=True)
if __name__=='__main__':main()
