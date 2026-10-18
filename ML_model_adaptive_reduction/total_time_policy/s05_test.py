"""Test the frozen selector, identical ML-off controls, and prior application."""
from s00_cost_common import *
from s02_collect import cases,measured,get_reference,claim

def initialize():
 p=HERE/'test_protocol.json'
 if p.exists():return READ(p)
 f=READ(HERE/'trained_model/freeze.json');assert f['complete']
 cs=cases(2011,'reserved',['dots','mixed','rank2','pinched'])
 cs+=products(2027,'reserved')
 # Formula families at every order retain a fresh parameter profile.
 for c in connected(2039,'reserved'):
  if c['topology_group'].startswith(('vacuum_one_mass','propagator_massless')) and exact(c) is not None:
   c['scope']='analytic_formula';cs.append(c)
 # Preserve the previously difficult three-loop scattering type in coverage.
 cs+=[c for c in connected(2053,'reserved') if c['topology_group']=='ladder_L3']
 protocol=dict(complete=True,cases=cs,methods=['raw_native','fixed','learned','previous'],repetitions=3,model_sha256=sha(HERE/'trained_model/freeze.json'),basis_sha256=sha(BLOCK/'extension/basis_cache.json'),sources={n:sha(HERE/n) for n in ['s00_cost_common.py','s01_runtime.py','s03_train.py','s05_test.py']},previous_sources={n:sha(BLOCK/n) for n in ['s00_common.py','s08_reduce.py','s10_validated_runtime.py']},policy='Freeze all choices before reserved tests. Rotate methods within each case on the same worker. Do not repeat unsuccessful first attempts. Retain all failures and unverified reference preparations.',scope='Native coupled requests through three loops; specified formulas and independent products through thirteen. Pentagon never enters training or validation.')
 assert len({c['id'] for c in cs})==len(cs)
 write(p,protocol);return protocol

def main(worker):
 p=initialize();assert sha(HERE/'trained_model/freeze.json')==p['model_sha256']
 assert all(sha(HERE/n)==s for n,s in p['sources'].items())
 for i,c in enumerate(p['cases']):
  dest=HERE/'coverage/reserved'/(c['id']+'.json')
  if dest.exists() or not claim(c,'reserved',worker):continue
  start=time.perf_counter();ref=get_reference(c);first={}
  for rep in range(p['repetitions']):
   methods=p['methods'];order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measured(c,m,rep,ref,'model_test')
    if not rep:first[m]=r
  row=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],family=c['topology_group'],shape=c.get('shape'),reference_success=ref['success'],reference_seconds=ref['preparation_seconds'],methods={m:dict(completed=r['success'],verified=r['independently_verified'],status=r.get('status'),seconds=r['complete_process_and_check_seconds'],model_used=r.get('model_used',False)) for m,r in first.items()},elapsed_seconds=time.perf_counter()-start)
  write(dest,row);print(json.dumps(dict(case=c['id'],verified={m:r['independently_verified'] for m,r in first.items()},seconds=row['elapsed_seconds'])),flush=True)
 write(HERE/('test_'+str(worker)+'_complete.json'),dict(complete=True,model_sha256=p['model_sha256']))
if __name__=='__main__':main(int(sys.argv[1]))
