"""Compare the integrated expert with ML-free choices and the preceding application."""
from s00_cost_common import *
from s02_collect import cases,measured,get_reference,claim

def initialize():
 p=HERE/'test_protocol.json'
 if p.exists():return READ(p)
 cs=cases(2311,'reserved')+cases(2317,'reserved')
 for profile in [2311,2317]:
  template=cases(profile,'reserved')[0]
  for rank,powers in [(2,[-1,-1]),(3,[-1,-2]),(4,[-1,-3]),(4,[-3,-1])]:
   c=copy.deepcopy(template);c.update(id=f'nonplanar_h{profile}_unseen_{-powers[0]}_{-powers[1]}_r{rank}',targets=[[1]*7+powers],shape='unseen_numerator')
   assert eligible(c);cs.append(c)
 for c in connected(2321,'reserved'):
  if c['topology_group'] in ['propagator_massive_L1','vacuum_all_mass_L3','propagator_massive_L3','vacuum_one_mass_L13','pentagon']:
   if exact(c) is not None:c['scope']='analytic_formula'
   cs.append(c)
 for c in connected(2321,'reserved'):
  if c['topology_group']=='propagator_massive_L2':
   n=len(c['definition']['propagators']);physical=c['definition']['physical_propagators'];a=[int(j<physical) for j in range(n)];a[physical]=-3
   c.update(id='massive_L2_h2321_rank3_guard',targets=[a],size=1,shape='rank3_guard');cs.append(c)
 wanted={('product_propagator_massive',4),('product_vacuum_all_mass',8),('product_ladder',12),('product_nonplanar_box',13)}
 cs += [c for c in products(2327,'reserved') if (c['topology_group'],len(c['definition']['loop_momenta'])) in wanted]
 assert len(cs)==34 and len({c['id'] for c in cs})==34
 f=READ(HERE/'trained_model/freeze.json');assert f['complete']
 pvalue=dict(complete=True,binary_sha256=sha(ROOT/'.tools/kira-sector-wide/kira'),cases=cs,methods=['raw_native','fixed','learned','previous'],repetitions=3,model_sha256=sha(HERE/'trained_model/freeze.json'),expert_sha256=sha(HERE/'trained_model/expert.json'),basis_sha256=sha(BLOCK/'extension/basis_cache.json'),sources={n:sha(HERE/n) for n in ['s00_cost_common.py','s01_runtime.py','s02_collect.py','s03_train.py','s05_test.py']},previous_sources={n:sha(BASE/n) for n in ['s00_cost_common.py','s01_runtime.py','s03_train.py','trained_model/freeze.json','trained_model/fixed.json']},expert_sources={n:sha(SPARSE/n) for n in ['s00_policy.py','s05_reduce.py']},policy='Freeze before the reserved profiles. Keep all failures, exact comparisons, and full process costs. Previous runs the actual preceding application. Fixed is the validation-best ML-free candidate.',scope='Twenty-four independent-profile targets covering all two-auxiliary numerator powers at ranks 2-4 in the nonplanar box, including eight requests with index vectors absent from training and validation, plus ten compatibility requests through thirteen loops.')
 write(p,pvalue);return pvalue

def main(worker):
 p=initialize();assert sha(HERE/'trained_model/freeze.json')==p['model_sha256']
 assert all(sha(HERE/n)==h for n,h in p['sources'].items())
 for i,c in enumerate(p['cases']):
  dest=HERE/'coverage/reserved'/(c['id']+'.json')
  if dest.exists() or not claim(c,'reserved',worker):continue
  start=time.perf_counter();ref=get_reference(c);first={}
  for rep in range(3):
   methods=p['methods'];order=methods[(i+rep)%4:]+methods[:(i+rep)%4]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measured(c,m,rep,ref,'model_test')
    if not rep:first[m]=r
  row=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],family=c['topology_group'],shape=c.get('shape'),reference_success=ref['success'],reference_seconds=ref['preparation_seconds'],methods={m:dict(completed=r['success'],verified=r['independently_verified'],status=r.get('status'),seconds=r['complete_process_and_check_seconds'],model_used=r.get('model_used',False)) for m,r in first.items()},elapsed_seconds=time.perf_counter()-start)
  write(dest,row);print(json.dumps(dict(case=c['id'],verified={m:r['independently_verified'] for m,r in first.items()},seconds=row['elapsed_seconds'])),flush=True)
 write(HERE/('test_'+str(worker)+'_complete.json'),dict(complete=True))

if __name__=='__main__':main(int(sys.argv[1]))
