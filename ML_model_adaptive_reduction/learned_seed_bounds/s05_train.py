"""Select a runtime cost model without reading reserved measurements."""
import json,math,time,warnings,platform
import sklearn
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from s00_inputs import *
import s01_runtime as rt

def dataset(split):
 protocol=rt.read(HERE/'protocol.json');rows=[];excluded=[]
 assert rt.read(HERE/split/'completion.json')['complete']
 for c in protocol['splits'][split]:
  paths=[HERE/split/(c['id']+'_'+a+'.json.gz') for a in ACTIONS]
  if not all(p.exists() for p in paths):excluded.append(dict(case=c['id'],reason='Reference or candidate collection incomplete'));continue
  r=[rt.read(p) for p in paths]
  if not all(z['reference_checked'] and z['success'] for z in r):excluded.append(dict(case=c['id'],reason='Some candidate did not complete with an exact result'));continue
  # Identity-only inputs do not enter training or speedup claims.
  coeff=r[0]['coefficients']
  if all(v=={t:'1'} for t,v in coeff.items()):excluded.append(dict(case=c['id'],reason='Identity-only reduction'));continue
  rows.append(dict(case=c,times=[z['complete_seconds'] for z in r]))
 write(HERE/split/'eligibility.json',dict(included=[r['case']['id'] for r in rows],excluded=excluded))
 return rows

def export(est,scaler=None):
 if isinstance(est,MLPRegressor):
  return dict(kind='mlp',weights=[a.tolist() for a in est.coefs_],bias=[a.tolist() for a in est.intercepts_],mean=scaler.mean_.tolist(),scale=scaler.scale_.tolist(),activation=est.activation)
 trees=est.estimators_ if hasattr(est,'estimators_') else [est]
 return dict(kind='forest',trees=[dict(left=e.tree_.children_left.tolist(),right=e.tree_.children_right.tolist(),feature=e.tree_.feature.tolist(),cut=e.tree_.threshold.tolist(),value=e.tree_.value[:,:,0].tolist()) for e in trees])

def main():
 start=time.perf_counter();train=dataset('training');valid=dataset('validation');assert len(train)>12 and len(valid)>8
 x=np.array([features(r['case']) for r in train]);xt=np.array([features(r['case']) for r in valid]);times=np.array([r['times'] for r in train]);vt=np.array([r['times'] for r in valid])
 y=np.log(times/times[:,[0]]);weight=np.sqrt(times[:,0]/np.median(times[:,0]));scaler=StandardScaler().fit(x)
 # Give fixed controls both training and validation data, including all actions.
 pooled=train+valid;global_cost=np.sum([r['times'] for r in pooled],axis=0);glob=ACTIONS[int(np.argmin(global_cost))];fixed={}
 for g in GRAPHS:
  rows=[r['times'] for r in pooled if r['case']['topology_group']==g]
  fixed[g]=ACTIONS[int(np.argmin(np.sum(rows,axis=0)))] if rows else glob
 base=np.array([ACTIONS.index(fixed[r['case']['topology_group']]) for r in valid]);index=np.arange(len(valid));fixed_cost=float(vt[index,base].sum())
 candidates=[]
 for depth in [2,3,5,8]:
  for leaf in [1,2,4]:
   candidates.append((f'tree_d{depth}_l{leaf}',DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=41),None))
 for cls,label in [(ExtraTreesRegressor,'extra_trees'),(RandomForestRegressor,'random_forest')]:
  for depth in [3,5,8]:
   candidates.append((f'{label}_d{depth}',cls(n_estimators=48,max_depth=depth,min_samples_leaf=2,random_state=41,n_jobs=1),None))
 for layers in [(16,),(32,),(32,16)]:
  for alpha in [.01,.1]:
   for activation in ['relu','tanh']:
    candidates.append((f'mlp_{layers}_{alpha}_{activation}',MLPRegressor(hidden_layer_sizes=layers,activation=activation,solver='lbfgs',alpha=alpha,max_iter=1500,random_state=41),scaler))
 results=[];best=None;best_cost=float('inf');checks=0
 for name,est,scale in candidates:
  tick=time.perf_counter()
  with warnings.catch_warnings(record=True) as warns:
   if scale is None:est.fit(x,y,sample_weight=weight);pred=est.predict(xt)
   else:est.fit(scale.transform(x),y);pred=est.predict(scale.transform(xt))
  model=export(est,scale);manual=np.array([rt.predict(model,a) for a in xt]);error=float(np.max(np.abs(manual-pred)));assert error<2e-6,(name,error);checks+=len(valid)*len(ACTIONS)
  pred=manual
  chosen=np.argmin(pred,axis=1)
  for gate in [0.,.03,.10,.20]:
   actions=np.where(pred[index,chosen]<pred[index,base]-gate,chosen,base)
   cost=float(vt[index,actions].sum());row=dict(name=name,gate=gate,seconds=cost,ratio_to_fixed=cost/fixed_cost,actions=[ACTIONS[i] for i in actions],fit_seconds=time.perf_counter()-tick,warnings=[str(w.message) for w in warns],prediction_max_error=error,parameters=est.get_params())
   results.append(row)
   if cost<best_cost:
    best_cost=cost;best=dict(model=model,model_name=name,gate=gate,fixed_by_graph=fixed,fixed_global=glob)
 for group in ['trained_model','model_test']: (HERE/group).mkdir(exist_ok=True)
 write(HERE/'trained_model/fixed.json',dict(fixed_global=glob,fixed_by_graph=fixed,source='Training and validation measured costs; no learned weights.'))
 best.update(actions=ACTIONS,features=FEATURE_NAMES,training_cases=[r['case']['id'] for r in train],validation_cases=[r['case']['id'] for r in valid],protocol_sha256=sha(HERE/'protocol.json'),inference_source_sha256=sha(HERE/'s01_runtime.py'),frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),domain='Listed graph structures, stated target bounds, rational kinematics, dimension symbolic; other domains need new tests.')
 domain={}
 for g in GRAPHS:
  group=[r['case'] for r in pooled if r['case']['topology_group']==g]
  if group:
   a=np.array([features(c) for c in group]);domain[g]=dict(signatures=sorted({signature(c) for c in group}),minimum=a.min(axis=0).tolist(),maximum=a.max(axis=0).tolist())
 best['domain']=domain
 # Target positions may change. Bound overall complexity, not incidence averages.
 best['bounded_features']=[5,6,7,21,25]
 write(HERE/'trained_model/freeze.json',best)
 out=dict(complete=True,training_cases=len(train),validation_cases=len(valid),candidate_fits=len(candidates),candidates=results,selected=best['model_name'],gate=best['gate'],native_validation_seconds=float(vt[:,0].sum()),fixed_validation_seconds=fixed_cost,learned_validation_seconds=best_cost,fixed_by_graph=fixed,fixed_global=glob,predictor_parity_checks=checks,training_seconds=time.perf_counter()-start,protocol_sha256=sha(HERE/'protocol.json'),model_sha256=sha(HERE/'trained_model/freeze.json'),excluded_training=len(rt.read(HERE/'protocol.json')['splits']['training'])-len(train),excluded_validation=len(rt.read(HERE/'protocol.json')['splits']['validation'])-len(valid))
 out['library_versions']=dict(python=platform.python_version(),numpy=np.__version__,scikit_learn=sklearn.__version__)
 write(HERE/'trained_model/selection.json',out);print(json.dumps({k:v for k,v in out.items() if k!='candidates'}),flush=True)
if __name__=='__main__':main()
