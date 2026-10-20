"""Matched complete-time tests and independent exact-domain coverage."""
from s00_direct_common import *
from s25_deploy_measure import measured
from s08_checks import sympy_reference
from s14_prepare import sha

def reference(c):
 if c['test_group']=='scaleless_vacuum':return dict(success=True,blocks=[dict(case=c,indices=list(range(len(c['definition']['propagators']))),result=dict(success=True,coefficients={label(t):{} for t in c['targets']},masters=[],reference='Homogeneity and dimensional continuation; native checks at one and two loops.'))])
 if c['test_group'] in ['vacuum_products','extended_vacuum']:return sympy_reference(c)
 if c['test_group']=='connected_vacuum':return current().run(c,'all_fixed')
 old=load('direct_old_reference',PRIOR/'s15_test.py');return old.reference(c)

def compare(c,r,ref):
 if not r.get('success') or not ref.get('success'):return False,0
 if c['test_group'] in ['lightlike','ordinary_tensor']:
  old=load('direct_old_compare',PRIOR/'s15_test.py');return old.compare(c,r,ref)
 return helper().compare(r,ref)

def main(worker):
 p=read(HERE/'final_protocol.json.gz');assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert sha(PRIOR/'trained_model/policy.json')==p['retained_model_sha256']
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'deployment_test'/(c['id']+'.json.gz')
  if dest.exists():continue
  ref=reference(c);assert ref['success'],c['id'];methods=['integrated'] if c['test_group'] in ['extended_vacuum','scaleless_vacuum'] else ['integrated','fixed','previous'];times={m:[] for m in methods};success={m:[] for m in methods};saved={};checks=0;failed_attempts={m:[] for m in methods};statuses={m:[] for m in methods}
  for rep in range(p['repetitions']):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    r,t=measured(c,method,worker,p['seconds_per_application']);ok,n=compare(c,r,ref)
    if r.get('success'):assert ok,(c['id'],method,'exact disagreement')
    attempts=[a for b in r.get('blocks',[]) for a in b['result'].get('attempts',[])];failed_attempts[method].append(sum(not a.get('success',False) for a in attempts));times[method].append(t);success[method].append(ok);checks+=n;statuses[method].append(r.get('status'));saved[method]=r
  row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),targets=c['size'],reference_success=True,reference=ref,times=times,success=success,statuses=statuses,failed_attempts=failed_attempts,median_seconds={m:statistics.median(v) for m,v in times.items()},checks=checks,results=saved);write(dest,row);print(json.dumps({k:v for k,v in row.items() if k in ['case','median_seconds','success']}),flush=True)
 write(HERE/f'deployment_test{worker}.json',dict(complete=True,protocol_sha256=sha(HERE/'final_protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
