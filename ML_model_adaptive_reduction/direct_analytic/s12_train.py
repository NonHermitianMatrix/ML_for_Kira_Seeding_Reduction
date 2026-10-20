"""Fit complete-cost trees with a separately learned failure admission guard."""
from s00_direct_common import *
ACTIONS=read(HERE/'actions.json')['actions']
from s03_cases import cases as native_cases
from s11_failure_guard import train as train_guard,gate
import numpy as np

def predict(t,x):
 while 'feature' in t:t=t['left'] if x[t['feature']]<=t['cut'] else t['right']
 return t['cost']

def rows(phase):
 out=[]
 for c in native_cases(phase):
  row=read(HERE/phase/(c['id']+'.json.gz'));ms=row['measurements']
  out.append(dict(case=c['id'],features=row['features'],costs=[statistics.median(x['application_seconds'] if x['verified'] else max(60.,x['application_seconds']) for x in ms[a]) for a in ACTIONS],verified=[all(x['verified'] for x in ms[a]) for a in ACTIONS]))
 return out

def main():
 assert all(read(HERE/f'collection{i}.json')['complete'] for i in [0,1])
 train=rows('training');val=rows('validation');namespace={'__name__':'vac_fit','np':np};source=(ROOT/'ML_model_adaptive_reduction/analytic_batch/s07_train.py').read_text();exec(source[source.index('def fit_tree('):source.index('def rows(')],namespace);fit_tree=namespace['fit_tree']
 X=np.array([r['features'] for r in train]);C=np.array([r['costs'] for r in train]);V=np.array([r['costs'] for r in val])
 safe=[a for a in range(3) if all(r['verified'][a] for r in train+val)];assert safe,'No validated fully successful anchor; do not deploy'
 fixed=min(safe,key=lambda a:V.sum(0)[a]);guard=train_guard(train);bounds=dict(minimum=X.min(0).tolist(),maximum=X.max(0).tolist(),failure_guard=guard);candidates=[];best=None
 for count in [1,12,32]:
  for depth in [1,2,3,4,5]:
   for minimum in [2,4,8]:
    rng=random.Random(6103);trees=[]
    for k in range(count):
     ids=np.arange(len(X)) if count==1 else np.array([rng.randrange(len(X)) for _ in range(len(X))]);trees.append(fit_tree(X,C,ids,depth,minimum,rng,count>1))
    for margin in [0.,.03,.08,.15]:
     for threshold in [0.,.05,.15,.3]:
      choices=[];redirects=0
      for row in val:
       scores=[statistics.mean(predict(t,row['features'])[j] for t in trees) for j in range(3)];j=min(range(3),key=scores.__getitem__)
       if scores[j]+.002>=scores[fixed]*(1-margin):j=fixed
       selected,info=gate(dict(bounds,failure_threshold=threshold),row['features'],j,fixed);redirects+=selected!=j;choices.append(selected)
      cost=sum(r['costs'][j]+.002 for r,j in zip(val,choices));bad=sum(not r['verified'][j] for r,j in zip(val,choices))
      r=dict(count=count,depth=depth,minimum=minimum,margin=margin,failure_threshold=threshold,cost=cost,unverified=bad,changes=sum(j!=fixed for j in choices),guard_redirects=redirects);candidates.append(r)
      if best is None or (bad,cost,count,depth,threshold)<(best[0]['unverified'],best[0]['cost'],best[0]['count'],best[0]['depth'],best[0]['failure_threshold']):best=(r,trees)
 enabled=best[0]['unverified']==0 and best[0]['cost']<float(V.sum(0)[fixed])*.99 and best[0]['changes']>0
 model=dict(bounds,complete=True,enabled=bool(enabled),actions=ACTIONS,fixed=ACTIONS[fixed],trees=best[1],margin=best[0]['margin'],failure_threshold=best[0]['failure_threshold'],selection=best[0],training_requests=len(train),validation_requests=len(val),fixed_validation_seconds=float(V.sum(0)[fixed]),safe_anchor_verified_requests=len(train)+len(val),objective='Complete process time; unverified choices cost at least 60 seconds; learned failure gate; 2 ms prediction allowance.')
 write(HERE/'trained_model/policy.json',model);write(HERE/'trained_model/fixed.json',dict(action=model['fixed']));write(HERE/'trained_model/selection.json.gz',dict(candidates=candidates,fixed_costs=dict(zip(ACTIONS,map(float,V.sum(0))))));write(HERE/'training/rows.json.gz',dict(training=train,validation=val))
 print(json.dumps({k:v for k,v in model.items() if k not in ['trees','minimum','maximum','failure_guard']}),flush=True)
if __name__=='__main__':main()
