"""Fit seed-cost predictors for one checked reduction per loop block."""
from s00_common import *

def predict(m,x):
 if m['kind'] in ['mlp','ridge']:
  v=[(a-b)/s for a,b,s in zip(x,m['mean'],m['scale'])]
  if m['kind']=='ridge':return [b+sum(a*c for a,c in zip(v,row)) for row,b in zip(m['coef'],m['intercept'])]
  for k,(w,b) in enumerate(zip(m['weights'],m['bias'])):
   v=[b[j]+sum(v[i]*w[i][j] for i in range(len(v))) for j in range(len(b))]
   if k<len(m['weights'])-1:v=[max(0.,a) for a in v]
  return v
 import struct
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x];scores=[0.]*len(ACTIONS)
 for t in m['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  for j,v in enumerate(t['value'][i]):scores[j]+=v/len(m['trees'])
 return scores

def choose(c,freeze):
 scores=predict(freeze['model'],features(c));anchor=freeze['selection']['anchor'];i=min(range(len(scores)),key=scores.__getitem__)
 return ACTIONS[i if scores[i]<scores[anchor]-freeze['selection']['margin'] else anchor],scores

def rows(split):
 out=[]
 for folder,reps in [('learned_seed_bounds',1),('portfolio_policy',1 if split=='training' else 2)]:
  root=ROOT/'ML_model_adaptive_reduction'/folder
  for c in READ(root/'protocol.json')['splits'][split]:
   paths=[[root/split/(c['id']+'_'+a+('_r'+str(r) if folder=='portfolio_policy' else '')+'.json.gz') for r in range(reps)] for a in ACTIONS]
   if not all(p.exists() for ps in paths for p in ps):continue
   rs=[[READ(p) for p in ps] for ps in paths]
   if not all(r['success'] for r in rs[0]):continue
   costs=[];failures=[]
   for group in rs:
    values=[]
    for r in group:
     ats=r.get('attempts',[])
     values.append(sum(a['complete_seconds'] for a in ats) if r['success'] else max(180.,sum(a['complete_seconds'] for a in ats)*3))
    costs.append(statistics.median(values));failures.append(sum(not r['attempts'][0]['success'] for r in group))
   assert min(costs)>0
   out.append(dict(case=canonical(c),costs=costs,first_failures=failures,sources=[str(p.relative_to(ROOT)) for ps in paths for p in ps]))
 return out

def train():
 import numpy as np
 from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
 from sklearn.neural_network import MLPRegressor
 from sklearn.linear_model import Ridge
 from sklearn.model_selection import GroupKFold
 from s01_families import initialize
 initialize();train=rows('training');val=rows('validation');start=time.perf_counter()
 X=np.array([features(r['case']) for r in train]);C=np.array([r['costs'] for r in train]);Y=np.clip(np.log(C/C[:,[0]]),-4,5)
 V=np.array([features(r['case']) for r in val]);VC=np.array([r['costs'] for r in val]);VF=np.array([r['first_failures'] for r in val]);mean=X.mean(0);scale=np.maximum(X.std(0),1e-6)
 fixed=int(VC.sum(0).argmin());write(HERE/'trained_model/fixed.json',dict(action=ACTIONS[fixed]))
 class ConsistentMLP(MLPRegressor):
  def _backprop(self,X,y,activations,deltas,coef_grads,intercept_grads):
   loss,cg,ig=super()._backprop(X,y,activations,deltas,coef_grads,intercept_grads)
   penalty=.5*self.alpha*sum(np.sum(w*w) for w in self.coefs_)/len(X)
   return (loss-penalty)*y.shape[1]+penalty,cg,ig
 def export(m,kind):
  if kind=='mlp':return dict(kind=kind,mean=mean.tolist(),scale=scale.tolist(),weights=[w.tolist() for w in m.coefs_],bias=[b.tolist() for b in m.intercepts_])
  if kind=='ridge':return dict(kind=kind,mean=mean.tolist(),scale=scale.tolist(),coef=m.coef_.tolist(),intercept=m.intercept_.tolist())
  return dict(kind='trees',trees=[dict(left=t.tree_.children_left.tolist(),right=t.tree_.children_right.tolist(),feature=t.tree_.feature.tolist(),cut=t.tree_.threshold.tolist(),value=t.tree_.value[:,:,0].tolist()) for t in m.estimators_])
 options=[];models={};parity=0
 definitions=[(kind,depth) for kind in ['forest','extra'] for depth in [3,6,10]]+[('ridge',1),('ridge',10)]+[('mlp',w) for w in [24,48,80]]
 groups=[inputs.signature(c['case']) for c in train]
 for kind,depth in definitions:
  def make():
   if kind in ['forest','extra']:return (RandomForestRegressor if kind=='forest' else ExtraTreesRegressor)(n_estimators=48,max_depth=depth,min_samples_leaf=3,n_jobs=1,random_state=1291)
   if kind=='ridge':return Ridge(alpha=depth)
   return ConsistentMLP(hidden_layer_sizes=(depth,depth),alpha=.3,solver='lbfgs',max_iter=500,random_state=1291)
  normalized=kind in ['mlp','ridge'];oof=np.zeros_like(Y)
  for tr,te in GroupKFold(n_splits=5).split(X,Y,groups):
   m=make();mu=X[tr].mean(0);sd=np.maximum(X[tr].std(0),1e-6);m.fit((X[tr]-mu)/sd if normalized else X[tr],Y[tr]);oof[te]=m.predict((X[te]-mu)/sd if normalized else X[te])
  m=make();m.fit((X-mean)/scale if normalized else X,Y);model=export(m,kind)
  expected=m.predict((X-mean)/scale if normalized else X)
  for x,y in zip(X,expected):assert np.max(np.abs(np.array(predict(model,x))-y))<1e-8;parity+=1
  scores=np.array([predict(model,x) for x in V]);name=kind+'_'+str(depth);models[name]=model
  write(HERE/'trained_model'/(name+'.json'),model)
  for anchor in sorted({0,fixed}):
   for margin in [0.,.05,.15,.3]:
    def ids(scores):return np.array([int(row.argmin()) if row.min()<row[anchor]-margin else anchor for row in scores])
    vi=ids(scores);oi=ids(oof);vr=float(VC[np.arange(len(V)),vi].sum()/VC[:,0].sum());cv=float(C[np.arange(len(X)),oi].sum()/C[:,0].sum())
    options.append(dict(candidate=name,anchor=anchor,margin=margin,validation_ratio=vr,group_cv_ratio=cv,validation_first_failures=int(VF[np.arange(len(V)),vi].sum()),score=max(vr,cv)))
 best=min(options,key=lambda x:x['score'])
 legacy=READ(general.HERE/'refit/trained_model/freeze.json');legacy_cost=float(sum(r['costs'][ACTIONS.index(choose(r['case'],legacy)[0])] for r in val)/VC[:,0].sum())
 # Select on independent historical validation, before either new profile is run.
 selected_new=bool(best['validation_ratio']<legacy_cost*.99 and best['score']<1)
 selected=best if selected_new else dict(legacy['selection'],candidate='previous_shared_model',validation_ratio=legacy_cost)
 model=models[best['candidate']] if selected_new else legacy['model']
 freeze=dict(complete=True,model=model,selection=selected,new_fit_selected=selected_new,best_new=best,previous_validation_ratio=legacy_cost,training_requests=len(train),validation_requests=len(val),features=FEATURE_NAMES,parity_checks=parity,fit_seconds=time.perf_counter()-start,options=options,sources=[r['sources'] for r in train],objective='Log ratio of summed native-attempt cost including recovery; unsuccessful full actions receive a penalty. No separate production reference reduction is included.',scope='All available historical training structures. Validation profiles remain separate. Profiles 1301 and 1307 are reserved.')
 write(HERE/'trained_model/freeze.json',freeze);write(HERE/'trained_model/selection.json',{k:v for k,v in freeze.items() if k not in ['model','sources','options']})
 write(HERE/'training/rows.json.gz',dict(training=train,validation=val))
 print(json.dumps({k:v for k,v in freeze.items() if k in ['selection','new_fit_selected','training_requests','validation_requests','fit_seconds','parity_checks']}),flush=True)

if __name__=='__main__':train()
