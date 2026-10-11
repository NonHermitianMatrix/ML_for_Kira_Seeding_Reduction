"""Train small equation-choice trees from exact dependency counts."""
import hashlib,time
import numpy as np
from s00_math import *
def fit(x,y,depth,minchild=8):
 nodes=[]
 def build(ids,level):
  n=len(ids);p=float(y[ids].sum());idx=len(nodes)
  nodes.append(dict(feature=-1,threshold=0,left=-1,right=-1,probability=(p+.5)/(n+1),rows=n,positive=int(p)))
  if level>=depth or n<2*minchild or p==0 or p==n:return idx
  parent=p*(n-p)/n;best=None;gain=0
  for j in range(x.shape[1]):
   vals=x[ids,j]
   for cut in np.unique(vals)[:-1]:
    mask=vals<=cut;nl=int(mask.sum());nr=n-nl
    if nl<minchild or nr<minchild:continue
    pl=float(y[ids[mask]].sum());pr=p-pl
    g=parent-pl*(nl-pl)/nl-pr*(nr-pr)/nr
    if g>gain+1e-10:gain=g;best=(j,float(cut),mask)
  if best:
   j,c,m=best;l=build(ids[m],level+1);r=build(ids[~m],level+1)
   nodes[idx].update(feature=j,threshold=c,left=l,right=r)
  return idx
 build(np.arange(len(y)),0);return nodes
def main():
 start=time.perf_counter();xx=[];yy=[];groups=0
 # Train exponent shapes up to total power nine. No mass profile or loop label.
 for r in [2,3,4]:
  for B in range(2,10):
   for b in compositions(B,r):
    pp=pairs(b)
    if len(pp)<2:continue
    costs=[]
    for p in pp:
     x,y=children(b,p);costs.append(len(teacher(x)[0]|teacher(y)[0]|{b}))
    for p,c in zip(pp,costs):xx.append(features(b,p));yy.append(int(c==min(costs)))
    groups+=1
 x=np.array(xx,dtype=float);y=np.array(yy,dtype=float)
 for depth in [4,8,12]:
  nodes=fit(x,y,depth)
  model=dict(kind="CART",features=FEATURES,nodes=nodes,maximum_depth=depth,training_groups=groups,training_rows=len(y),positive_rows=int(y.sum()),maximum_training_power=9,label="Tied minimum size of union of two recursively selected dependency sets. Sufficient local teacher, not a global optimum.",probability="Smoothed leaf frequency; not calibrated confidence.",loop_feature=False,training_seconds=time.perf_counter()-start)
  write(HERE/"trained_model"/("depth%d.json"%depth),model)
 write(HERE/"training/summary.json",dict(groups=groups,rows=len(y),positives=int(y.sum()),seconds=time.perf_counter()-start,teacher_cache=str(teacher.cache_info()),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
 print(json.dumps(dict(training_rows=len(y),groups=groups,seconds=time.perf_counter()-start)),flush=True)
if __name__=="__main__":main()
