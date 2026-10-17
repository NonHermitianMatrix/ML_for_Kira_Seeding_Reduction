"""Fit complete-time predictors and choose deployment on separate validation costs."""
import json,math,statistics,time
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
from s00_runtime import HERE,ACTIONS,rt,inputs,feature,predict,choose,save

def records(stage):
 p=rt.read(HERE/stage/'protocol.json');out=[]
 for c in p['cases']:
  if not (HERE/'references'/(c['id']+'.json.gz')).exists():continue
  if not rt.read(HERE/'references'/(c['id']+'.json.gz'))['success']:continue
  times=[];complete=[]
  for a in ACTIONS:
   actual=p.get('canonical_partitions',{}).get(c['id'],{}).get(a,a)
   paths=[HERE/stage/(c['id']+'_'+actual+f'_r{j}.json.gz') for j in range(p['repetitions'])]
   if not all(q.exists() for q in paths):break
   rows=[rt.read(q) for q in paths];ok=all(r['success'] for r in rows)
   times.append(statistics.median(r['complete_seconds'] for r in rows) if ok else max(300.,sum(r['complete_seconds'] for r in rows)));complete.append(ok)
  if len(times)==len(ACTIONS) and any(complete):out.append(dict(case=c,x=feature(c),times=times,complete=complete))
 return out

def export(m):
 trees=m.estimators_ if hasattr(m,'estimators_') else [m]
 return dict(trees=[dict(left=t.tree_.children_left.tolist(),right=t.tree_.children_right.tolist(),feature=t.tree_.feature.tolist(),cut=t.tree_.threshold.tolist(),value=t.tree_.value[:,:,0].tolist()) for t in trees])

def main():
 assert not (HERE/'trained_model/freeze.json').exists(),'A frozen policy must not be overwritten.'
 start=time.perf_counter();tr=records('training');va=records('validation');assert len(tr)>=20 and len(va)>=20
 x=np.array([r['x'] for r in tr]);y=np.log(np.array([r['times'] for r in tr]));y-=y[:,0:1]
 weights=np.sqrt(np.array([min(r['times']) for r in tr]));weights/=weights.mean()
 domain={};fixed={};fixed_off={};vo=records('validation_off')
 for g in sorted({r['case']['topology_group'] for r in tr+va}):
  rows=[r for r in tr if r['case']['topology_group']==g]
  if rows:
   xs=np.array([r['x'] for r in rows]);domain[g]=dict(signatures=sorted({inputs.signature(r['case']) for r in rows}),minimum=xs.min(0).tolist(),maximum=xs.max(0).tolist())
  v=[r for r in va if r['case']['topology_group']==g];tot=[sum(r['times'][i] for r in v) for i in range(len(ACTIONS))]
  fixed[g]=ACTIONS[min(range(len(ACTIONS)),key=lambda i:tot[i])]
  v=[r for r in vo if r['case']['topology_group']==g]
  if not v:domain.pop(g,None)
  tot=[sum(r['times'][i] for r in v) for i in range(len(ACTIONS))];fixed_off[g]=ACTIONS[min(range(len(ACTIONS)),key=lambda i:tot[i])]
 inputs.write(HERE/'trained_model/fixed.json',dict(by_graph=fixed,off_by_graph=fixed_off,selection='Separate minimum sums of validation batch costs with filters enabled and with all ML disabled; failures cost at least 300 seconds.'))
 baseline=sum(r['times'][ACTIONS.index(fixed[r['case']['topology_group']])] for r in va)
 candidates=[];best=None;parity=0
 for kind in ['tree','forest','extra']:
  for depth in [2,4,6]:
   for leaf in [1,3]:
    kw=dict(max_depth=depth,min_samples_leaf=leaf,random_state=805)
    m=DecisionTreeRegressor(**kw) if kind=='tree' else (RandomForestRegressor if kind=='forest' else ExtraTreesRegressor)(n_estimators=32,n_jobs=1,**kw)
    m.fit(x,y,sample_weight=weights);model=export(m)
    for row,expected in zip(x,m.predict(x)):
     assert np.allclose(predict(model,row),expected,rtol=1e-12,atol=1e-12);parity+=1
    for gate in [0.,.02,.05,.1]:
     f=dict(model=model,gate=gate,fixed_by_graph=fixed,domain=domain);total=0;choices=[]
     for r in va:
      a,_=choose(r['case'],f);total+=r['times'][ACTIONS.index(a)];choices.append(a)
     meta=dict(kind=kind,depth=depth,min_leaf=leaf,gate=gate,validation_cost=total,ratio=total/baseline,choices=choices)
     candidates.append(meta)
     if best is None or total<best['validation_cost']:best=meta|dict(model=model)
 assert best
 enabled=best['validation_cost']<.97*baseline
 f=dict(model=best.pop('model'),enabled=enabled,gate=best['gate'],fixed_by_graph=fixed,domain=domain,selected=best,validation_fixed_cost=baseline,minimum_gain=.03,training_cases=len(tr),validation_cases=len(va),feature_names=inputs.FEATURE_NAMES+['distinct_dots','distinct_ranks','dot_range','rank_range','mean_dot_rank_product'],actions=ACTIONS,loss='Weighted squared error of log complete-time ratios to whole batches; failed actions carry at least 300 seconds.',parity_checks=parity,fitting_seconds=time.perf_counter()-start,frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),test_profiles=[721,722],test_repetitions=5,sources={n:inputs.sha(HERE/n) for n in ['s00_runtime.py','s01_cases.py','s02_collect.py','s04_fit.py','s05_test.py','s06_pipeline.py']},native_sha256=inputs.sha(rt.BINARY),filter_source_sha256=inputs.sha(HERE/'fixed_inputs.json'))
 inputs.write(HERE/'trained_model/freeze.json',f);save(HERE/'trained_model/candidates.json.gz',dict(candidates=candidates,training_ids=[r['case']['id'] for r in tr],validation_ids=[r['case']['id'] for r in va]))
 print('FROZEN',json.dumps({k:v for k,v in f.items() if k not in ['model','domain','sources','feature_names']}),flush=True)

if __name__=='__main__':main()
