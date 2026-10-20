"""Fit reduction costs and admit ML only after separate validation."""
from s00_reconstruction_common import *
from s10_cases import cases,features
from s13_cost_decision import choose
import numpy as np
import sklearn
from sklearn.ensemble import ExtraTreesRegressor

def rows(phase,actions):
 out=[];omitted=[]
 for c in cases(phase):
  records={}
  for a in actions:
   p=HERE/phase/(c['id']+'_'+a+'.json.gz')
   if p.exists():records[a]=read(p)
  if len(records)!=len(actions) or not records['previous']['verified']:
   omitted.append(c['id']);continue
  assert all(np.allclose(r['features'],features(c),rtol=0,atol=1e-12) for r in records.values()),c['id']
  base=records['previous']['application_seconds'];cost=[];failure=[]
  for a in actions:
   r=records[a];failed=r.get('failure_fraction',float(not r['verified']))
   # An unsuccessful new backend must still pay for the exact fallback.
   cost.append(r['application_seconds']+base*failed)
   failure.append(float(failed))
  out.append(dict(case=c['id'],group=helper().inputs.signature(c),x=features(c),cost=cost,failure=failure,base=base))
 return out,omitted

def export(model):
 trees=[]
 for e in model.estimators_:
  t=e.tree_;trees.append(dict(left=t.children_left.tolist(),right=t.children_right.tolist(),feature=t.feature.tolist(),cut=t.threshold.tolist(),value=t.value[:,:,0].tolist()))
 return dict(trees=trees)

def main():
 assert os.environ.get('JOB_ID')
 for phase in ['training','validation']:
  for w in [0,1]:assert read(HERE/(phase+str(w)+'_complete.json'))['complete']
 cfg=read(HERE/'actions.json');actions=cfg['actions'];train,omitted_train=rows('training',actions);valid,omitted_valid=rows('validation',actions)
 assert len(train)>=16 and len(valid)>=8,(len(train),len(valid))
 x=np.array([r['x'] for r in train],dtype=float)
 y=np.array([[v/r['base'] for v in r['cost']]+r['failure'] for r in train])
 weights=np.array([r['base'] for r in train])
 totals=[sum(r['cost'][i] for r in valid) for i in range(len(actions))]
 fixed=actions[min(range(len(actions)),key=totals.__getitem__)]
 fixed_by_structure={}
 for group in {r['group'] for r in valid}:
  v=[sum(r['cost'][i] for r in valid if r['group']==group) for i in range(len(actions))]
  fixed_by_structure[group]=actions[min(range(len(actions)),key=v.__getitem__)]
 initial=dict(actions=actions,fixed=fixed,fixed_by_structure=fixed_by_structure,minimum=x.min(axis=0).tolist(),maximum=x.max(axis=0).tolist(),enabled=False)
 def evaluate(policy,learned=True):
  seconds=0.;failures=0;selected=[]
  for r in valid:
   a,_=choose(policy,r['x'],learned,r['group']);i=actions.index(a)
   seconds+=r['cost'][i];failures+=int(r['failure'][i]>0);selected.append(a)
  return dict(seconds=seconds,failed_first_attempts=failures,selected=selected)
 fixed_result=evaluate(initial,False);trials=[];best=None
 for depth in [2,4,6]:
  for leaf in [2,4]:
   estimator=ExtraTreesRegressor(n_estimators=32,max_depth=depth,min_samples_leaf=leaf,random_state=26821,n_jobs=1)
   estimator.fit(x,y,sample_weight=weights);model=export(estimator)
   for margin in [0.,.05,.1,.2]:
    policy=dict(initial,enabled=True,model=model,margin=margin,failure_limit=.02)
    result=evaluate(policy);trial=dict(depth=depth,min_leaf=leaf,margin=margin,**result);trials.append(trial)
    if result['failed_first_attempts']==0 and (best is None or result['seconds']<best[0]):
     best=(result['seconds'],policy,trial)
 assert best is not None
 chosen=best[1];chosen['enabled']=best[0]<fixed_result['seconds']*.97
 chosen.update(complete=True,settings=cfg['settings'],deadline=cfg['deadline'],validation_fixed=fixed_result,validation_selected=best[2],training_cases=[r['case'] for r in train],validation_cases=[r['case'] for r in valid],omitted_training=omitted_train,omitted_validation=omitted_valid,training_objective='Squared relative complete-cost error weighted by baseline seconds; failed attempts include baseline recovery cost.',admission='At least 3 percent validation saving over the matched fixed control and no failed selected validation attempt.',feature_names=list(helper().inputs.FEATURE_NAMES)+['maximum_rational_numerator_bits','maximum_rational_denominator_bits'],random_state=26821,packages=dict(python=sys.version,numpy=np.__version__,scikit_learn=sklearn.__version__),cases_source_sha256=sha(HERE/'s10_cases.py'),actions_sha256=sha(HERE/'actions.json'),source_sha256={f.name:sha(f) for f in HERE.glob('s*.py') if 4<=int(f.name[1:3])<=15})
 write(HERE/'trained_model/policy.json',chosen)
 fixed_config={k:chosen[k] for k in ['actions','fixed','fixed_by_structure','minimum','maximum','settings','deadline']}
 fixed_config['enabled']=False
 write(HERE/'trained_model/fixed.json',fixed_config)
 write(HERE/'trained_model/deployment.json',dict(enabled=chosen['enabled'],configuration='policy.json' if chosen['enabled'] else 'fixed.json'))
 write(HERE/'training_summary.json',dict(complete=True,training=len(train),validation=len(valid),fixed=fixed,enabled=chosen['enabled'],fixed_validation=fixed_result,best_validation=best[2],trials=trials,omitted_training=omitted_train,omitted_validation=omitted_valid))
 print('cost model complete',chosen['enabled'],fixed,round(fixed_result['seconds'],3),round(best[0],3),flush=True)
if __name__=='__main__':main()
