"""Fit cost models, then select safe family-specific deployment on validation."""
from s00_common import *
from s01_application import predict
import math,statistics
import numpy as np
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor

def export(m):
 ts=m.estimators_ if hasattr(m,'estimators_') else [m]
 return dict(trees=[dict(left=t.tree_.children_left.tolist(),right=t.tree_.children_right.tolist(),feature=t.tree_.feature.tolist(),cut=t.tree_.threshold.tolist(),value=t.tree_.value[:,:,0].tolist()) for t in ts])
def rows(c,where,reps=1):
 out=[]
 for a in ACTIONS:
  ps=[where/(c['id']+'_'+a+('_r'+str(r) if where.parent==HERE else '')+'.json.gz') for r in range(reps)]
  if not all(p.exists() for p in ps):return None
  rs=[read(p) for p in ps];out.append(statistics.median(r['complete_seconds'] if r['success'] else max(180.,r['complete_seconds']*3) for r in rs))
 return out

def main():
 d=read(HERE/'protocol.json');d['methods']=['native','fixed','learned','previous','production'];d['reserved_timer_excludes_administrative_storage_scan']=True;write(HERE/'protocol.json',d);X=[];Y=[];sources=[];training_cases=[]
 old=ROOT/'ML_model_adaptive_reduction/learned_seed_bounds';historical=read(old/'protocol.json')['splits']['training']
 for c,p in [(c,old/'training') for c in historical]+[(c,HERE/'training') for c in d['splits']['training']]:
  y=rows(c,p)
  if y is None:continue
  X.append(features(c));Y.append([math.log(v/y[0]) for v in y]);sources.append(dict(case=c['id'],folder=str(p.relative_to(ROOT))));training_cases.append(c)
 assert X
 candidates=[];tick=time.perf_counter();parity=0
 for kind in ['tree','forest','extra']:
  for depth in [2,4,6]:
   kw=dict(max_depth=depth,min_samples_leaf=2,random_state=1101)
   m=DecisionTreeRegressor(**kw) if kind=='tree' else (RandomForestRegressor if kind=='forest' else ExtraTreesRegressor)(n_estimators=32,n_jobs=1,**kw)
   m.fit(X,Y);out=export(m)
   for x in X:
    assert np.max(np.abs(np.array(predict(out,x))-m.predict([x])[0]))<1e-9;parity+=1
   name=kind+'_d'+str(depth)+'.json';write(HERE/'trained_model'/name,dict(model=out,kind=kind,depth=depth));candidates.append((name,out))
 family_candidates={}
 # Each family has its own cost scale and can need a different response to
 # extra denominator or numerator powers. Fit a small local expert using
 # invariant target-complexity features, without line-position shortcuts.
 projection=[6,7,5,25,26,8,9,18,19,21]
 for g in sorted({c['topology_group'] for c in d['splits']['training']}):
  cs=[c for c in d['splits']['training'] if c['topology_group']==g];local=[(c,rows(c,HERE/'training')) for c in cs];local=[(c,y) for c,y in local if y is not None]
  if len(local)<2:continue
  xx=[[features(c)[i] for i in projection] for c,y in local];yy=[[math.log(v/y[0]) for v in y] for c,y in local]
  m=DecisionTreeRegressor(max_depth=1,min_samples_leaf=1,random_state=1101);m.fit(xx,yy);out=export(m)
  for t in out['trees']:t['feature']=[projection[i] if i>=0 else i for i in t['feature']]
  for c,y in local:
   assert np.max(np.abs(np.array(predict(out,features(c)))-m.predict([[features(c)[i] for i in projection]])[0]))<1e-9;parity+=1
  name='family_'+g+'.json';write(HERE/'trained_model'/name,dict(model=out,kind='family_cost_tree',projection=projection,training=[c['id'] for c,y in local]));family_candidates[g]=[(name,out)]
 domains={};validation={};enabled=0
 for g in sorted({c['topology_group'] for c in d['splits']['validation']}):
  cs=[c for c in d['splits']['validation'] if c['topology_group']==g];valid=[(c,rows(c,HERE/'validation',2)) for c in cs];valid=[(c,y) for c,y in valid if y is not None]
  if not valid:continue
  cost=np.array([y for c,y in valid]);base=int(np.argmin(cost.sum(axis=0)));fixed=float(cost[:,base].sum());options=[]
  for name,m in candidates+family_candidates.get(g,[]):
   scores=[predict(m,features(c)) for c,y in valid]
   for margin in [0.,.03,.08]:
    ids=[min(range(len(ACTIONS)),key=s.__getitem__) for s in scores];ids=[i if s[i]<s[base]-margin else base for i,s in zip(ids,scores)]
    total=sum(cost[i,j] for i,j in enumerate(ids));options.append(dict(model_file=name,margin=margin,choices=ids,seconds=float(total)))
  best=min(options,key=lambda r:r['seconds']);enable=len(valid)>=2 and best['seconds']<.97*fixed
  xs=np.array([features(c) for c in training_cases+cs if inputs.signature(c)==inputs.signature(cs[0])]);entry=dict(action=ACTIONS[base],enabled=enable,model_file=best['model_file'],margin=best['margin'],minimum=xs.min(axis=0).tolist(),maximum=xs.max(axis=0).tolist(),validation_ratio=best['seconds']/fixed,graph=g)
  old_cost=sum(statistics.median(read(HERE/'validation'/(c['id']+'_previous_r'+str(r)+'.json.gz'))['complete_seconds'] for r in range(2)) for c,y in valid)
  entry['deploy']=(best['seconds'] if enable else fixed)<.97*old_cost;entry['previous_seconds']=old_cost
  domains[inputs.signature(cs[0])]=entry;enabled+=enable
  validation[g]=dict(cases=[c['id'] for c,y in valid],costs=cost.tolist(),fixed_seconds=fixed,chosen=best,enabled=enable,options=options)
 write(HERE/'trained_model/fixed.json',dict(domains=domains,selection='Three percent validation improvement over the best fixed action, with two completed target shapes. Unknown cases use native bounds.'))
 write(HERE/'validation/selection.json',validation)
 fitting_seconds=time.perf_counter()-tick
 from s15_confirm import confirm
 confirmed,confirmation_seconds=confirm();enabled=sum(e['enabled'] for e in read(HERE/'trained_model/fixed.json')['domains'].values())
 write(HERE/'trained_model/freeze.json',dict(complete=True,confirmation_cases=confirmed,confirmation_seconds=confirmation_seconds,training=sources,training_count=len(X),validation=[c['id'] for c in d['splits']['validation']],test=[c['id'] for c in d['splits']['reserved']],enabled_domains=enabled,fitting_seconds=fitting_seconds,parity_checks=parity,model_sha256={p.name:inputs.sha(p) for p in (HERE/'trained_model').glob('*.json') if p.name!='freeze.json'},application_sha256=inputs.sha(HERE/'s01_application.py'),production_sha256=inputs.sha(HERE/'s08_reduce.py')))
 print('FROZEN',len(X),'training cases',enabled,'learned domains',flush=True)
if __name__=='__main__':main()
