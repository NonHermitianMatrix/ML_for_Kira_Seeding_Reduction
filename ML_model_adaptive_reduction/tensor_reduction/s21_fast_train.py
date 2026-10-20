"""Fit complete-cost trees and select conservative choices on separate validation inputs."""
from s00_tensor_common import *
from s03_cases import cases
import numpy as np

def rows(phase):
 out=[]
 for c in cases(phase):
  row=read(HERE/('fast_'+phase)/(c['id']+'.json.gz'));ms=row['measurements']
  out.append(dict(case=c['id'],features=row['features'],costs=[statistics.median(x['application_seconds'] if x['verified'] else max(60.,x['application_seconds']) for x in ms[a]) for a in ACTIONS],verified=[all(x['verified'] for x in ms[a]) for a in ACTIONS]))
 return out

def main():
 assert all(read(HERE/f'fast_collection{i}_complete.json')['complete'] for i in [0,1])
 train=rows('training');val=rows('validation');namespace={'__name__':'vac_fit','np':np};source=(ROOT/'ML_model_adaptive_reduction/analytic_batch/s07_train.py').read_text();exec(source[source.index('def fit_tree('):source.index('def rows(')],namespace);fit_tree=namespace['fit_tree']
 X=np.array([r['features'] for r in train]);C=np.array([r['costs'] for r in train]);V=np.array([r['costs'] for r in val]);fixed=int(V.sum(0).argmin());candidates=[];best=None
 for count in [1,24]:
  for depth in [1,2,3,4]:
   for minimum in [2,4,8]:
    rng=random.Random(7193);trees=[]
    for k in range(count):
     ids=np.arange(len(X)) if count==1 else np.array([rng.randrange(len(X)) for _ in range(len(X))])
     trees.append(fit_tree(X,C,ids,depth,minimum,rng,count>1))
    for margin in [0.,.03,.08,.15]:
     choices=[]
     for row in val:
      scores=[statistics.mean(predict(t,row['features'])[j] for t in trees) for j in range(len(ACTIONS))];j=min(range(len(ACTIONS)),key=scores.__getitem__)
      if scores[j]+.001>=scores[fixed]*(1-margin):j=fixed
      if any(v<a or v>b for v,a,b in zip(row['features'],X.min(0),X.max(0))):j=fixed
      choices.append(j)
     cost=sum(r['costs'][j]+.001 for r,j in zip(val,choices));bad=sum(not r['verified'][j] for r,j in zip(val,choices))
     r=dict(count=count,depth=depth,minimum=minimum,margin=margin,cost=cost,unverified=bad,changes=sum(j!=fixed for j in choices));candidates.append(r)
     if best is None or (bad,cost,count,depth)<(best[0]['unverified'],best[0]['cost'],best[0]['count'],best[0]['depth']):best=(r,trees)
 enabled=best[0]['unverified']<=sum(not r['verified'][fixed] for r in val) and best[0]['cost']<float(V.sum(0)[fixed])*.99 and best[0]['changes']>0
 model=dict(complete=True,enabled=bool(enabled),actions=ACTIONS,fixed=ACTIONS[fixed],trees=best[1],minimum=X.min(0).tolist(),maximum=X.max(0).tolist(),margin=best[0]['margin'],selection=best[0],training_requests=len(train),validation_requests=len(val),fixed_validation_seconds=float(V.sum(0)[fixed]),objective='Complete process time with exact verification required; failed choices cost at least 60 seconds; 1 ms prediction allowance in selection.')
 write(HERE/'trained_model/fast_policy.json',model);write(HERE/'trained_model/fast_fixed.json',dict(action=model['fixed']));write(HERE/'trained_model/fast_selection.json',dict(candidates=candidates,fixed_costs=dict(zip(ACTIONS,map(float,V.sum(0))))));write(HERE/'fast_training/rows.json.gz',dict(training=train,validation=val))
 print(json.dumps({k:v for k,v in model.items() if k not in ['trees','minimum','maximum']}),flush=True)
if __name__=='__main__':main()
