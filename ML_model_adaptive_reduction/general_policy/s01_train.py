"""Fit shared predictors and validate transfer by withholding physical families."""
from s00_common import *
import numpy as np
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from s02_application import predict

def load_rows(split):
 result=[]
 for folder,reps in [('learned_seed_bounds',1),('portfolio_policy',1 if split=='training' else 2)]:
  base=ROOT/'ML_model_adaptive_reduction'/folder
  for c in READ(base/'protocol.json')['splits'][split]:
   if held_out(c):continue
   paths=[[base/split/(c['id']+'_'+a+('_r'+str(r) if folder=='portfolio_policy' else '')+'.json.gz') for r in range(reps)] for a in ACTIONS]
   if not all(p.exists() for group in paths for p in group):continue
   rs=[[READ(p) for p in group] for group in paths]
   if not all(r['success'] for r in rs[0]):continue
   costs=[statistics.median(r['complete_seconds'] if r['success'] else max(180.,r['complete_seconds']*3) for r in group) for group in rs]
   result.append(dict(case=c,costs=costs,sources=[str(p.relative_to(ROOT)) for group in paths for p in group]))
 return result

def export(m,kind,mean,scale):
 if kind=='mlp':return dict(kind=kind,mean=mean.tolist(),scale=scale.tolist(),weights=[w.tolist() for w in m.coefs_],bias=[v.tolist() for v in m.intercepts_])
 if kind=='ridge':return dict(kind=kind,mean=mean.tolist(),scale=scale.tolist(),coef=m.coef_.tolist(),intercept=m.intercept_.tolist())
 trees=m.estimators_ if hasattr(m,'estimators_') else [m]
 return dict(kind='trees',trees=[dict(left=t.tree_.children_left.tolist(),right=t.tree_.children_right.tolist(),feature=t.tree_.feature.tolist(),cut=t.tree_.threshold.tolist(),value=t.tree_.value[:,:,0].tolist()) for t in trees])

def main():
 freeze_protocol();start=time.perf_counter();train=load_rows('training');val=load_rows('validation');assert train and val
 X=np.array([features(r['case']) for r in train]);C=np.array([r['costs'] for r in train]);Y=np.clip(np.log(C/C[:,[0]]),-4,5)
 V=np.array([features(r['case']) for r in val]);VC=np.array([r['costs'] for r in val]);mean=X.mean(0);scale=np.maximum(X.std(0),1e-6)
 groups=[inputs.signature(r['case']) for r in train];fixed=int(np.argmin(VC.sum(0)));write(HERE/'trained_model/fixed.json',dict(action=ACTIONS[fixed]))
 defs=[(k,d) for k in ['tree','forest','extra'] for d in [2,4,7]]+[('ridge',1),('ridge',10),('mlp',24),('mlp',48)]
 options=[];parity=0
 for kind,depth in defs:
  def make():
   kw=dict(max_depth=depth,min_samples_leaf=3,random_state=1201)
   if kind=='tree':return DecisionTreeRegressor(**kw)
   if kind in ['forest','extra']:return (RandomForestRegressor if kind=='forest' else ExtraTreesRegressor)(n_estimators=48,n_jobs=1,**kw)
   if kind=='ridge':return Ridge(alpha=depth)
   return MLPRegressor(hidden_layer_sizes=(depth,depth),activation='relu',solver='lbfgs',alpha=.1,max_iter=500,random_state=1201)
  normalized=kind in ['ridge','mlp'];xx=(X-mean)/scale if normalized else X
  oof=np.zeros_like(Y)
  for tr,te in GroupKFold(n_splits=min(5,len(set(groups)))).split(X,Y,groups):
   fm=make();mu=X[tr].mean(0);sd=np.maximum(X[tr].std(0),1e-6)
   fm.fit((X[tr]-mu)/sd if normalized else X[tr],Y[tr]);oof[te]=fm.predict((X[te]-mu)/sd if normalized else X[te])
  m=make();m.fit(xx,Y);model=export(m,kind,mean,scale)
  for x in X:
   expected=m.predict([(x-mean)/scale if normalized else x])[0]
   assert np.max(np.abs(predict(model,x)-expected))<1e-8;parity+=1
  scores=np.array([predict(model,x) for x in V]);name=kind+'_'+str(depth)+'.json';write(HERE/'trained_model'/name,model)
  for anchor in [0,fixed]:
   for margin in [0.,.05,.12,.25]:
    def ids(s):
     chosen=s.argmin(1);return np.array([j if row[j]<row[anchor]-margin else anchor for j,row in zip(chosen,s)])
    vi=ids(scores);oi=ids(oof)
    vratio=float(VC[np.arange(len(V)),vi].sum()/VC[:,0].sum());oratio=float(C[np.arange(len(C)),oi].sum()/C[:,0].sum())
    options.append(dict(file=name,anchor=anchor,margin=margin,validation_ratio=vratio,group_cv_ratio=oratio,validation_changes=int(sum(vi!=0)),score=max(vratio,oratio)))
 best=min(options,key=lambda r:r['score']);model=READ(HERE/'trained_model'/best['file'])
 # The trained candidate is tested independently even if validation does not support replacing the deployed workflow.
 result=dict(complete=True,model=model,selection=best,replace_default=best['score']<.97,training_count=len(train),validation_count=len(val),fitting_seconds=time.perf_counter()-start,features=FEATURE_NAMES,parity_checks=parity,
  training=[dict(case=r['case']['id'],loops=len(r['case']['definition']['loop_momenta']),group=inputs.signature(r['case']),sources=r['sources']) for r in train],
  validation=[r['case']['id'] for r in val],options=options,physical_holdouts=READ(HERE/'protocol.json')['excluded_from_training_and_validation'])
 write(HERE/'trained_model/freeze.json',result)
 write(HERE/'trained_model/selection.json',{k:v for k,v in result.items() if k not in ['model','training','options']})
 print(json.dumps({k:v for k,v in result.items() if k in ['selection','replace_default','training_count','validation_count','fitting_seconds','parity_checks']}),flush=True)
if __name__=='__main__':main()
