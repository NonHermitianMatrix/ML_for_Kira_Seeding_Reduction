"""Add less constrained tree fits before any reserved test is run."""
import json,shutil
import numpy as np
import s05_study as study
from s05_study import HERE,features,medians,write,freeze,sha

def main():
 assert not list((HERE/'model_test').glob('*.json.gz')),'Reserved tests have already started'
 cache={}
 def cached_medians(case,split,reps):
  key=(case['id'],split,reps)
  if key not in cache:cache[key]=medians(case,split,reps)
  return cache[key]
 study.medians=cached_medians
 cases=json.loads((HERE/'cases.json').read_text())['cases'];cs=[c for c in cases if c['split']=='training']
 x=np.array([features(c) for c in cs]);times=np.array([medians(c,'training',3) for c in cs]);y=np.log(times/times[:,0,None])
 p=HERE/'trained_model/candidates.json';record=json.loads(p.read_text())
 initial=HERE/'development/initial_candidates.json'
 if not initial.exists():shutil.copyfile(p,initial)
 old=HERE/'trained_model/freeze.json';backup=HERE/'development/initial_model_freeze.json'
 if not backup.exists():shutil.copyfile(old,backup)
 record['models']=[m for m in record['models'] if '_leaf1' not in m['name']]
 for depth in [2,4,6]:
  nodes=[]
  def make(ids,level):
   index=len(nodes);nodes.append(dict(feature=-1,value=y[ids].mean(axis=0).tolist(),rows=len(ids)))
   if level==depth or len(ids)<2:return index
   best=None;loss=float(((y[ids]-y[ids].mean(axis=0))**2).sum())
   for f in range(x.shape[1]):
    u=np.unique(x[ids,f])
    for cut in (u[:-1]+u[1:])/2:
     mask=x[ids,f]<=cut;a,b=ids[mask],ids[~mask]
     new=float(((y[a]-y[a].mean(axis=0))**2).sum()+((y[b]-y[b].mean(axis=0))**2).sum())
     if new<loss-1e-10:loss=new;best=(f,float(cut),a,b)
   if best:
    f,cut,a,b=best;left=make(a,level+1);right=make(b,level+1);nodes[index].update(feature=f,threshold=cut,left=left,right=right)
   return index
  make(np.arange(len(cs)),0)
  record['models'].append(dict(name=f'tree{depth}_leaf1',type='tree',nodes=nodes,minimum_child_batches=1))
 record['extension_source_sha256']=sha(__file__);write(p,record)
 freeze(cases)
 print('Twelve candidate models compared before reserved tests',flush=True)
if __name__=='__main__':main()
