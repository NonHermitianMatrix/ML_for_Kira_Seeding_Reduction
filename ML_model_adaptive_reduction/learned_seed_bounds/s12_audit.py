"""Audit stored reductions and attribution without rerunning Kira."""
import collections,json
from s00_inputs import *
import s01_runtime as rt

def main():
 protocol=rt.read(HERE/'protocol.json');fit=rt.read(HERE/'trained_model/selection.json');freeze=rt.read(HERE/'trained_model/freeze.json');assert fit['complete']
 assert fit['model_sha256']==sha(HERE/'trained_model/freeze.json')
 assert fit['protocol_sha256']==freeze['protocol_sha256']==sha(HERE/'protocol.json')
 assert freeze['inference_source_sha256']==sha(HERE/'s01_runtime.py')
 assert protocol['binary']==sha(rt.BINARY)
 ids={s:{c['id'] for c in cs} for s,cs in protocol['splits'].items()}
 assert not(ids['training']&ids['validation'] or ids['training']&ids['reserved'] or ids['validation']&ids['reserved'])
 assert set(freeze['training_cases'])<=ids['training'] and set(freeze['validation_cases'])<=ids['validation']
 definitions={s:{json.dumps([c['definition'],sorted(c['targets'])],sort_keys=True) for c in cs} for s,cs in protocol['splits'].items()}
 assert not(definitions['training']&definitions['reserved'] or definitions['validation']&definitions['reserved'])
 cases={c['id']:c for cs in protocol['splits'].values() for c in cs};counts=collections.Counter();failures=[];checked=set();cache={}
 for folder in ['training','validation','model_test','application_test']:
  for p in (HERE/folder).glob('*.json.gz'):
   r=rt.read(p);counts[folder]+=1
   if not r['success']:failures.append(str(p.relative_to(HERE)));continue
   ref=rt.read(HERE/'references'/(r['case']+'.json.gz'));got=r['coefficients'];want=ref['coefficients'];assert set(got)==set(want),p
   for t,row in got.items():
    for m in set(row)|set(want[t]):
     a,b=row.get(m,'0'),want[t].get(m,'0');counts['coefficient_checks']+=1
     key=(a,b)
     if key not in checked:
      if a!=b:
       import sympy as sp
       for v in [a,b]:
        if v not in cache:cache[v]=sp.sympify(v.replace('^','**'),rational=True)
       assert sp.cancel(cache[a]-cache[b])==0,(p,t,m)
      checked.add(key)
   assert r.get('reference_coefficients_supplied') is False,p
   if folder!='application_test':
    assert r['no_other_ml'] and all(a['learned_algebra_disabled'] and a['equation_mode']=='off' and a['policy']=='native' and a['binary_sha256']==protocol['binary'] for a in r['attempts'])
   if folder=='model_test':
    if r['method']=='learned':
     action,scores=rt.choose(cases[r['case']],freeze);assert r['first_action']==action and r['scores']==scores,p
     assert r['model_sha256']==fit['model_sha256']
    else:assert r['scores'] is None and r['decision_seconds']==r['model_loading_seconds']==0 and r['model_sha256'] is None
 # Check that an unsupported structure and an out-of-range request cannot use the predictor.
 import copy
 probe=copy.deepcopy(cases[freeze['training_cases'][0]]);probe['definition']['propagators'][0]['momentum']='unsupported_momentum'
 assert rt.choose(probe,freeze)==('native',None)
 probe=copy.deepcopy(cases[freeze['training_cases'][0]]);probe['targets'][0][0]+=100
 assert rt.choose(probe,freeze)==('native',None)
 result=dict(complete=True,all_successful_outputs_exact=True,failed_files=failures,counts=dict(counts),distinct_coefficient_pairs=len(checked),disjoint_physical_split_inputs=True,unique_physical_inputs={s:len(v) for s,v in definitions.items()},no_earlier_models_in_primary_comparison=True,production_choice_reproduced=True,domain_checks=True,model_sha256=fit['model_sha256'],protocol_sha256=sha(HERE/'protocol.json'))
 write(HERE/'coefficient_audit.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
