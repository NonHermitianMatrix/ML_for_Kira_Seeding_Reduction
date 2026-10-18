"""Fit trees that minimize measured completion cost rather than label error."""
from s00_cost_common import *

def leaf(tree,x):
 while 'feature' in tree:tree=tree['left'] if x[tree['feature']]<=tree['cut'] else tree['right']
 return tree

def choose(c,basis,f):
 if basis is None:return 'raw_native',None
 if f.get('enabled') is False:return f['fixed_action'],None
 x=features(c,basis)
 # The guard uses only structural and target ranges, never family names.
 if any(x[j]<f['minimum'][j]-1e-9 or x[j]>f['maximum'][j]+1e-9 for j in f['guard_features']):return 'raw_native',None
 rows=[leaf(t,x) for t in f['trees']];costs=[math.fsum(r['cost'][i] for r in rows)/len(rows) for i in range(len(ACTIONS))]
 base=f['anchor'];i=min(range(len(ACTIONS)),key=costs.__getitem__)
 if costs[i]+f['decision_allowance_seconds']>=costs[base]*(1-f['margin']):i=base
 return ACTIONS[i],costs

def fit_tree(X,C,ids,depth,minimum,rng,subset=False):
 import numpy as np
 costs=C[ids].mean(0);node=dict(cost=costs.tolist(),samples=len(ids));base=float(C[ids].sum(0).min())
 if depth==0 or len(ids)<2*minimum:return node
 best=None;features_=range(X.shape[1])
 if subset:features_=rng.choice(X.shape[1],max(8,int(X.shape[1]**.5)*2),replace=False)
 for j in features_:
  values=np.unique(X[ids,j])
  if len(values)>17:values=np.unique(np.quantile(values,np.linspace(0,1,17)))
  for cut in (values[1:]+values[:-1])/2:
   left=ids[X[ids,j]<=cut];right=ids[X[ids,j]>cut]
   if min(len(left),len(right))<minimum:continue
   loss=float(C[left].sum(0).min()+C[right].sum(0).min())
   if best is None or loss<best[0]-1e-9:best=(loss,int(j),float(cut),left,right)
 if best is None or best[0]>=base-.002*len(ids):return node
 _,j,cut,left,right=best
 return dict(feature=j,cut=cut,left=fit_tree(X,C,left,depth-1,minimum,rng,subset),right=fit_tree(X,C,right,depth-1,minimum,rng,subset))

def main():
 import numpy as np
 from s02_collect import initialize
 p=initialize();cache=READ(BLOCK/'extension/basis_cache.json');rows={};start=time.perf_counter()
 for phase in ['training','validation']:
  data=[]
  for c in p[phase]:
   assert (HERE/'coverage'/phase/(c['id']+'.json')).exists()
   costs=[];fail=[];verified=[]
   for a in ACTIONS:
    rs=[READ(HERE/phase/(c['id']+'_'+a+'_r'+str(j)+'.json.gz')) for j in range(p[phase+'_repetitions'])]
    costs.append(statistics.median(r['complete_process_and_check_seconds'] if r['independently_verified'] else max(220.,r['complete_process_and_check_seconds']) for r in rs))
    fail.append(sum(r.get('failed_attempts',0) for r in rs));verified.append(all(r['independently_verified'] for r in rs))
   data.append(dict(case=c,features=features(c,basis_for(c,cache)),costs=costs,failed_attempts=fail,verified=verified))
  rows[phase]=data
 write(HERE/'training/rows.json.gz',rows)
 tr=rows['training'];val=rows['validation'];X=np.array([r['features'] for r in tr]);C=np.array([r['costs'] for r in tr]);VC=np.array([r['costs'] for r in val]);fixed=int(VC.sum(0).argmin());totals=VC.sum(0)
 # Native is always available. Failures keep a completion penalty and are retained.
 guards=list(range(5))+[6,7,10,11,13,14,15,16,25,26,len(FEATURE_NAMES)-1]
 common=dict(minimum=X.min(0).tolist(),maximum=X.max(0).tolist(),guard_features=guards,features=FEATURE_NAMES,decision_allowance_seconds=.002)
 candidates=[];models={}
 for depth in [1,2,3,4,5]:
  for minimum in [2,4,7]:
   for count in [1,16]:
    rng=np.random.RandomState(1913);trees=[]
    for k in range(count):
     ids=np.arange(len(X)) if count==1 else rng.randint(0,len(X),len(X))
     trees.append(fit_tree(X,C,ids,depth,minimum,rng,count>1))
    name=f'd{depth}_n{minimum}_t{count}'
    for anchor in sorted({0,fixed}):
     for margin in [0.,.03,.08,.15]:
      f=dict(common,trees=trees,anchor=anchor,margin=margin)
      ids=[ACTIONS.index(choose(r['case'],basis_for(r['case'],cache),f)[0]) for r in val]
      cost=sum(r['costs'][i] for r,i in zip(val,ids));fail=sum(not r['verified'][i] for r,i in zip(val,ids));retries=sum(r['failed_attempts'][i] for r,i in zip(val,ids))
      changed=sum(i!=fixed for i in ids);tag=name+f'_a{anchor}_m{margin}'
      models[tag]=f;candidates.append(dict(name=tag,cost_seconds=cost,unverified=fail,failed_attempts=retries,changed=changed,trees=count,depth=depth,minimum=minimum))
 # Require a measured validation improvement over a fixed policy to enable ML.
 best=min(candidates,key=lambda r:(r['unverified'],r['cost_seconds'],r['trees'],r['depth']))
 fallback=dict(common,trees=[dict(cost=(C.mean(0)).tolist(),samples=len(X))],anchor=fixed,margin=1.)
 enabled=best['unverified']<=sum(not r['verified'][fixed] for r in val) and best['cost_seconds']+.002*len(val)<.985*totals[fixed]
 selected=models[best['name']] if enabled else fallback
 selected.update(complete=True,enabled=bool(enabled),fixed_action=ACTIONS[fixed],selection=best,training_requests=len(tr),validation_requests=len(val),validation_native_seconds=float(totals[ACTIONS.index('raw_native')]),validation_fixed_seconds=float(totals[fixed]),validation_selected_seconds=best['cost_seconds'] if enabled else float(totals[fixed]),fit_seconds=time.perf_counter()-start,objective='Sum of measured complete process and exact-check seconds, including retries. Unverified completions receive max(220 seconds, elapsed cost). Trees split by the decrease in action cost.',basis_sha256=sha(BLOCK/'extension/basis_cache.json'),training_sha256=sha(HERE/'training/rows.json.gz'))
 # Disabled models cause no feature extraction or tree inference at runtime.
 write(HERE/'trained_model/freeze.json',selected);write(HERE/'trained_model/fixed.json',dict(action=ACTIONS[fixed]));write(HERE/'trained_model/selection.json',dict(candidates=candidates,selected={k:v for k,v in selected.items() if k not in ['trees','minimum','maximum']},validation_all_action_costs=dict(zip(ACTIONS,map(float,totals)))))
 print(json.dumps({k:v for k,v in selected.items() if k in ['enabled','selection','fixed_action','validation_native_seconds','validation_fixed_seconds','validation_selected_seconds','fit_seconds','training_requests','validation_requests']}),flush=True)
if __name__=='__main__':
 main()
 inputs.module('refined_time_test_setup',HERE/'s05_test.py').initialize()
