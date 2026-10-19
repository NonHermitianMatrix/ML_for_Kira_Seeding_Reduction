"""Fit a cost-sensitive recurrence policy on independent kinematic profiles."""
from s00_fast_common import *
from s01_fast_recurrence import reduce as recurrence
from s03_fast_runtime import recurrence_features
import random
ACTIONS=['largest','smallest','first','last']

def cases(profile,split):
 old=legacy();poly=old.h.inputs.module('pivot_training_polygons',PRIOR/'s03_cases.py').polygon;out=[];rng=random.Random(profile)
 for n in [2,3,4,5]:
  for index in range(14):
   c=poly(n,profile,1);targets=[]
   for b in range(1+(index%3==0)):
    a=[1]*n
    for _ in range(1+index%6):a[rng.randrange(n)]+=1
    targets.append(a)
   c.update(id=f'pivot_n{n}_h{profile}_t{index}',targets=targets,size=len(targets),split=split);out.append(c)
 return out

def collect(profile,split):
 out=[]
 for c in cases(profile,split):
  file=HERE/'training'/split/(c['id']+'.json.gz')
  if file.exists():out.append(read(file));continue
  timings={a:[] for a in ACTIONS};reference=None;states={}
  for rep in range(3):
   order=ACTIONS[rep:]+ACTIONS[:rep]
   for action in order:
    start=time.perf_counter();r=recurrence(c,pivot=action,backend='gmp',deadline=time.perf_counter()+8);elapsed=time.perf_counter()-start
    assert r is not None,(c['id'],action)
    if reference is None:reference=r['coefficients']
    assert r['coefficients']==reference,(c['id'],action)
    timings[action].append(elapsed);states[action]=r['recurrence_states']
  row=dict(case=c,features=recurrence_features(c),costs=[statistics.median(timings[a]) for a in ACTIONS],times=timings,states=states,exact_equality=True,coefficients_sha256=hashlib.sha256(json.dumps(reference,sort_keys=True).encode()).hexdigest());write(file,row);out.append(row)
 print(json.dumps(dict(profile=profile,rows=len(out))),flush=True);return out

def fit_tree(X,C,ids,depth,minimum):
 import numpy as np
 costs=C[ids].mean(0);node=dict(cost=costs.tolist(),samples=len(ids));best=None;base=float(C[ids].sum(0).min())
 if depth==0 or len(ids)<2*minimum:return node
 for j in range(X.shape[1]):
  values=np.unique(X[ids,j])
  if len(values)>15:values=np.unique(np.quantile(values,np.linspace(0,1,15)))
  for cut in (values[1:]+values[:-1])/2:
   left=ids[X[ids,j]<=cut];right=ids[X[ids,j]>cut]
   if min(len(left),len(right))<minimum:continue
   loss=float(C[left].sum(0).min()+C[right].sum(0).min())
   if best is None or loss<best[0]:best=(loss,j,float(cut),left,right)
 if best is None or best[0]>=base-.0001*len(ids):return node
 _,j,cut,left,right=best
 return dict(feature=j,cut=cut,left=fit_tree(X,C,left,depth-1,minimum),right=fit_tree(X,C,right,depth-1,minimum))

def predict(tree,x):
 while 'feature' in tree:tree=tree['left'] if x[tree['feature']]<=tree['cut'] else tree['right']
 return tree['cost']

def main():
 assert read(HERE/'pilot.json')['complete']
 import numpy as np
 training=collect(2611,'training')+collect(2617,'training');validation=collect(2621,'validation')
 X=np.array([r['features'] for r in training]);C=np.array([r['costs'] for r in training]);V=np.array([r['costs'] for r in validation]);fixed=int(V.sum(0).argmin());candidates=[];best=None
 for depth in [1,2,3,4,5]:
  for minimum in [3,6,10]:
   tree=fit_tree(X,C,np.arange(len(X)),depth,minimum)
   for margin in [0.,.03,.1]:
    indices=[];tick=time.perf_counter()
    for row in validation:
     costs=predict(tree,row['features']);j=min(range(4),key=costs.__getitem__)
     if costs[j]+.0001>=costs[fixed]*(1-margin):j=fixed
     indices.append(j)
    overhead=time.perf_counter()-tick;total=sum(row['costs'][j] for row,j in zip(validation,indices))+overhead
    r=dict(depth=depth,minimum=minimum,margin=margin,total_seconds=total,inference_seconds=overhead,changes=sum(j!=fixed for j in indices));candidates.append(r)
    if best is None or total<best[0]:best=(total,tree,r)
 enabled=best[0]<.98*float(V.sum(0)[fixed]) and best[2]['changes']>0
 freeze=dict(complete=True,enabled=enabled,actions=ACTIONS,fixed=ACTIONS[fixed],trees=[best[1]],minimum=X.min(0).tolist(),maximum=X.max(0).tolist(),margin=best[2]['margin'],allowance=.0001,training_requests=len(training),validation_requests=len(validation),selected=best[2],fixed_validation_seconds=float(V.sum(0)[fixed]),learned_validation_seconds=best[0],objective='Measured exact recurrence seconds plus prediction overhead. Freeze before application-level reserved testing.')
 write(HERE/'trained_model/recurrence.json',freeze);write(HERE/'trained_model/selection.json',dict(candidates=candidates,complete=True));print(json.dumps({k:v for k,v in freeze.items() if k!='trees'}),flush=True)
if __name__=='__main__':main()
