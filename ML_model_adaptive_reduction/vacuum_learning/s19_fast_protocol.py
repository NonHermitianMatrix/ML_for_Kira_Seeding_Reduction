"""Freeze a new complete-time comparison after a request-output optimization."""
from s00_vac_common import *
from s04_cases import vacuum_case

def main():
 assert all(read(HERE/f'test{w}_complete.json')['complete'] for w in [0,1])
 original=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in original['source_sha256'].items())
 assert sha(HERE/'trained_model/policy.json')==original['model_sha256']
 cases=[];prop=load('vac_fast_prop_cases',PRIOR/'s03_prop_cases.py');q=ROOT/'ML_model_adaptive_reduction/loop_coverage13';tri=load('vac_fast_tri_cases',q/'s03_cases.py')
 for L in [1,3,7,13]:
  for kind,maker in [('vacuum',vacuum_case),('propagator',prop.case)]:
   c=maker(L,'chain',6073);c['test_group']=kind;cases.append(c)
  c=tri.tree_case(L,'chain',6073,True);c['test_group']='triangle';cases.append(c)
 for kind,maker in [('vacuum',vacuum_case),('propagator',prop.case)]:
  c=maker(13,'branched',6077,count=128);c['test_group']=kind;cases.append(c)
 # Eight new batch sets, from positions unused in any fitting or earlier reserved test.
 rng=random.Random(6101);pool=[];powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4]
 while len(pool)<48:
  n=rng.choice([1,2,2,3,4]);p=tuple(sorted(rng.sample(powers,n)))
  if p not in pool:pool.append(p)
 h=batch.legacy().h
 for kind in ['double_box','nonplanar_box']:
  for i in range(40,44):
   c=h.inputs.case(kind,6079,'rank2','reserved_output');ts=[[1]*7+[-a,-b] for a,b in pool[i]]
   c.update(id=f'output_{kind}_h6079_p{i}',targets=ts,size=len(ts),test_group='native',scope='native_batch');cases.append(batch.canonical(c))
 write(HERE/'output_protocol.json.gz',dict(complete=True,repetitions=3,seconds_per_application=18,cases=cases,model_sha256=original['model_sha256'],first_protocol_sha256=sha(HERE/'protocol.json.gz'),source_sha256={n:sha(HERE/n) for n in ['s17_output_budget.py','s18_fast_runtime.py','s19_fast_protocol.py','s20_fast_test.py','s21_fast_analyze.py']},runtime_file_budget_bytes=512*1024,budget_source='Part of the existing per-application transient reserve, separate from the permanent four-MiB study budget.'))
 print(json.dumps(dict(output_protocol=True,requests=len(cases),model_unchanged=True)),flush=True)
if __name__=='__main__':main()
