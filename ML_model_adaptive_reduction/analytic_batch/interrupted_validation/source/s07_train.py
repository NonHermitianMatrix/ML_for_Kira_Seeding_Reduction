"""Train cost-sensitive trees on complete fresh-process reduction times."""
from s00_batch_common import *
from s03_cases import batches
import random

def fit_tree(X,C,ids,depth,minimum,rng,random_features=False):
 import numpy as np
 node=dict(cost=C[ids].mean(0).tolist(),samples=len(ids));baseline=float(C[ids].sum(0).min())
 if depth==0 or len(ids)<2*minimum:return node
 best=None;columns=list(range(X.shape[1]))
 if random_features:rng.shuffle(columns);columns=columns[:max(5,len(columns)//2)]
 for j in columns:
  values=np.unique(X[ids,j])
  for cut in (values[1:]+values[:-1])/2:
   left=ids[X[ids,j]<=cut];right=ids[X[ids,j]>cut]
   if min(len(left),len(right))<minimum:continue
   loss=float(C[left].sum(0).min()+C[right].sum(0).min())
   if best is None or loss<best[0]-1e-9:best=(loss,int(j),float(cut),left,right)
 if best is None or best[0]>=baseline-.002*len(ids):return node
 _,j,cut,left,right=best
 return dict(feature=j,cut=cut,left=fit_tree(X,C,left,depth-1,minimum,rng,random_features),right=fit_tree(X,C,right,depth-1,minimum,rng,random_features))

def rows(phase,profiles,reps):
 out=[]
 for profile in profiles:
  for c in batches(profile,phase):
   assert read(HERE/'references'/(c['id']+'.json.gz'))['success'],c['id']
   rs=[[read(HERE/phase/(c['id']+'_'+a+'_r'+str(rep)+'.json.gz')) for rep in range(reps)] for a in ACTIONS]
   out.append(dict(case=c,features=features(c),costs=[statistics.median(r['complete_process_and_check_seconds'] if r['independently_verified'] else max(250.,r['complete_process_and_check_seconds']) for r in group) for group in rs],verified=[all(r['independently_verified'] for r in group) for group in rs]))
 return out

def main():
 import numpy as np
 for phase in ['training','validation']:
  for worker in [0,1]:assert read(HERE/(phase+'_'+str(worker)+'_complete.json'))['complete']
 train=rows('training',[3011,3019],1);val=rows('validation',[3037],2)
 X=np.array([r['features'] for r in train]);C=np.array([r['costs'] for r in train]);V=np.array([r['costs'] for r in val]);fixed=int(V.sum(0).argmin());candidates=[];best=None
 for count in [1,16]:
  for depth in [1,2,3,4]:
   for minimum in [2,4,8]:
    rng=random.Random(3007);trees=[]
    for k in range(count):
     ids=np.arange(len(X)) if count==1 else np.array([rng.randrange(len(X)) for _ in range(len(X))])
     trees.append(fit_tree(X,C,ids,depth,minimum,rng,count>1))
    for margin in [0.,.03,.08]:
     choices=[];tick=time.perf_counter()
     for row in val:
      costs=[statistics.mean(predict(t,row['features'])[j] for t in trees) for j in range(len(ACTIONS))];j=min(range(len(ACTIONS)),key=costs.__getitem__)
      if costs[j]+.002>=costs[fixed]*(1-margin):j=fixed
      choices.append(j)
     inference=time.perf_counter()-tick;cost=sum(r['costs'][j] for r,j in zip(val,choices))+inference
     r=dict(trees=count,depth=depth,minimum=minimum,margin=margin,cost=cost,unverified=sum(not row['verified'][j] for row,j in zip(val,choices)),changes=sum(j!=fixed for j in choices),inference_seconds=inference)
     candidates.append(r)
     if best is None or (r['unverified'],r['cost'],count,depth)<(best[0]['unverified'],best[0]['cost'],best[0]['trees'],best[0]['depth']):best=(r,trees)
 enabled=best[0]['unverified']<=sum(not r['verified'][fixed] for r in val) and best[0]['cost']<.98*float(V.sum(0)[fixed]) and best[0]['changes']>0
 model=dict(complete=True,enabled=bool(enabled),actions=ACTIONS,fixed=ACTIONS[fixed],trees=best[1],minimum=X.min(0).tolist(),maximum=X.max(0).tolist(),margin=best[0]['margin'],allowance=.002,training_requests=len(train),validation_requests=len(val),selection=best[0],fixed_validation_seconds=float(V.sum(0)[fixed]),objective='Complete process and exact verification time, with unsuccessful outcomes assigned at least 250 seconds. No reference coefficients enter prediction or reduction.')
 write(HERE/'training/rows.json.gz',dict(training=train,validation=val));write(HERE/'trained_model/initial_policy.json',model);write(HERE/'trained_model/policy.json',model);write(HERE/'trained_model/fixed.json',dict(action=model['fixed']));write(HERE/'trained_model/selection.json',dict(candidates=candidates,fixed_costs=dict(zip(ACTIONS,map(float,V.sum(0))))))
 print(json.dumps({k:v for k,v in model.items() if k not in ['trees','minimum','maximum']}),flush=True)
if __name__=='__main__':main()
