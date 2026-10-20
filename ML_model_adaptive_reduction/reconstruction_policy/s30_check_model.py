"""Check exported predictions and the complete entry point before reserved tests."""
from s00_reconstruction_common import *
from s13_cost_decision import scores
from s14_train import rows
from s06_measure import measured
from s20_reference import reference
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor

def main():
 assert os.environ.get('JOB_ID')
 p=read(HERE/'trained_model/policy.json');t=read(HERE/'training_summary.json')
 train,_=rows('training',p['actions']);valid,_=rows('validation',p['actions'])
 best=t['best_validation']
 x=np.array([r['x'] for r in train]);y=np.array([[v/r['base'] for v in r['cost']]+r['failure'] for r in train])
 estimator=ExtraTreesRegressor(n_estimators=32,max_depth=best['depth'],min_samples_leaf=best['min_leaf'],random_state=26821,n_jobs=1)
 estimator.fit(x,y,sample_weight=np.array([r['base'] for r in train]))
 checked=train+valid;pred=estimator.predict(np.array([r['x'] for r in checked]))
 error=max(abs(float(a)-b) for r,v in zip(checked,pred) for a,b in zip(v,scores(p['model'],r['x'])))
 assert error<1e-12,error
 fixed=read(HERE/'trained_model/fixed.json');assert 'model' not in fixed
 maker=load('reconstruction_smoke_cases',PREVIOUS/'s03_cases.py')
 cases=[c for c in maker.cases('development') if c['id'].endswith('_0')][:2]
 h=helper()
 sunrise=h.inputs.case('sunrise',27803,'corner','development');sunrise['test_group']='native';cases.append(sunrise)
 exact=next(c for c in read(PREVIOUS/'final_protocol.json.gz')['cases'] if c['test_group']=='vacuum_products')
 cases.append(exact)
 exact_checks=load('reconstruction_smoke_exact',PREVIOUS/'s27_deploy_test.py')
 records=[]
 for c in cases:
  ref=exact_checks.reference(c) if c.get('test_group')=='vacuum_products' else reference(c)
  assert ref.get('success'),c['id']
  for method in ['previous','fixed','integrated']:
   r,elapsed=measured(c,method,0,90,entry='s15_deploy.py')
   ok,n=exact_checks.compare(c,r,ref);assert ok,(c['id'],method,r.get('status'))
   records.append(dict(case=c['id'],method=method,application_seconds=elapsed,verified=ok,checks=n,action=r.get('reconstruction_action'),decision=r.get('reconstruction_decision')))
 write(HERE/'entry_checks.json',dict(complete=True,maximum_prediction_difference=error,prediction_requests=len(checked),applications=records,source_sha256={f.name:sha(f) for f in HERE.glob('s*.py') if int(f.name[1:3])<=24},model_sha256={n:sha(HERE/'trained_model'/n) for n in ['policy.json','fixed.json','deployment.json']}))
 print('Export and complete-entry checks passed',len(records),'applications',flush=True)
if __name__=='__main__':main()
