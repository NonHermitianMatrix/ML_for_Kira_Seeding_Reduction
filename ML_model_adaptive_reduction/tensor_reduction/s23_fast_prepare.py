"""Train on the revised arithmetic and freeze a fresh final application test."""
from s00_tensor_common import *
from s03_cases import case

def main():
 assert read(HERE/'fast_arithmetic_checks.json')['complete']
 from s21_fast_train import main as train
 train();old=previous();h=old.batch.legacy().h;families=h.inputs.module('tensor_final_products',h.BLOCK/'s01_families.py');tests=[]
 for k,(P,e) in enumerate([(2,1),(2,2),(3,1),(4,1)]):
  for j,(r,d,b) in enumerate([(1,2,2),(2,3,3),(3,1,2),(4,2,2)]):
   c=case(P,e,7801+8*k+j,rank=r,dots=d,count=b,seed=400+k*8+j);c['test_group']='tensor';tests.append(c)
 for P,e,mass in [(2,1,'massless'),(2,2,'mixed'),(3,1,'mixed'),(4,1,'mixed')]:
  c=case(P,e,7867+P+e,rank=3,dots=1,count=2,mass=mass,seed=431);c['test_group']='other_masses';tests.append(c)
 for L in range(2,14):
  blocks=[case(2,1,7901+L,rank=2,dots=2,count=2,seed=443) for _ in range(L)]
  c=families.compose(blocks,'tensor_final_product_L'+str(L),'reserved');c['test_group']='products';tests.append(c)
 rng=random.Random(6101);pool=[];powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4]
 while len(pool)<52:
  n=rng.choice([1,2,2,3,4]);v=tuple(sorted(rng.sample(powers,n)))
  if v not in pool:pool.append(v)
 for kind in ['double_box','nonplanar_box']:
  for i in range(48,52):
   c=h.inputs.case(kind,7949,'rank2','reserved_tensor_final');ts=[[1]*7+[-a,-b] for a,b in pool[i]]
   c.update(id=f'tensor_final_native_{kind}_p{i}',targets=ts,size=len(ts),test_group='native',scope='native_batch');tests.append(old.batch.canonical(c))
 for L in [1,3,7,13]:
  maker=load('tensor_final_vacuum_regression',PRIOR/'s04_cases.py');c=maker.vacuum_case(L,'branched',7963);c['test_group']='previous_exact';tests.append(c)
 first=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in first['source_sha256'].items())
 write(HERE/'fast_protocol.json.gz',dict(complete=True,repetitions=3,seconds_per_application=18,cases=tests,first_protocol_sha256=sha(HERE/'protocol.json.gz'),source_sha256={p.name:sha(p) for p in HERE.glob('s*.py') if int(p.name[1:3])<=12 or 16<=int(p.name[1:3])<=25 or int(p.name[1:3])==27},model_sha256=sha(HERE/'trained_model/fast_policy.json'),fixed_sha256=sha(HERE/'trained_model/fast_fixed.json'),prior_model_sha256=sha(PRIOR/'trained_model/policy.json'),prior_entry_sha256=sha(PRIOR/'s18_fast_runtime.py'),objective=first['objective']))
 print(json.dumps(dict(final_frozen=True,requests=len(tests),model_enabled=read(HERE/'trained_model/fast_policy.json')['enabled'])),flush=True)
if __name__=='__main__':main()
