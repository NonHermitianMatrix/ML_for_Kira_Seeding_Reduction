"""Fit cheap runtime predictions; require a gain over a graph-specific control."""
from s00_triangle_common import *

def predict(trees,x):
 scores=None
 for t in trees:
  j=0
  while t['left'][j]>=0:j=t['left'][j] if x[t['feature'][j]]<=t['cut'][j] else t['right'][j]
  if scores is None:scores=[0.]*len(t['value'][j])
  for i,v in enumerate(t['value'][j]):scores[i]+=v/len(trees)
 return scores

def choose(c,m,learned=True):
 group=c.get('topology_group');ts=c['targets']
 if group not in m['fixed'] or not prior().reconstruction_processor():return 'baseline'
 if len(ts)>6 or max(sum(max(-v,0) for v in a) for a in ts)>4 or max(sum(max(v-1,0) for v in a) for a in ts)>1:return 'baseline'
 action=m['fixed'][group]
 if learned and m['enabled']:
  from s07_collect import features
  scores=predict(m['trees'],features(c));k=m['actions'].index(action);j=min(range(len(scores)),key=scores.__getitem__)
  if scores[j]<scores[k]*(1-m['margin']):action=m['actions'][j]
 return action

def main():
 import numpy as np
 from sklearn.ensemble import ExtraTreesRegressor
 cfg=read(HERE/'learning_protocol.json');actions=cfg['actions'];rows={}
 for phase in ['training','validation']:
  assert all(read(HERE/(phase+str(w)+'_complete.json'))['complete'] for w in [0,1])
  rows[phase]=[read(p) for p in sorted((HERE/phase).glob('*.json.gz'))]
  assert all(r['reference_success'] and all(v['verified'] for v in r['actions'].values()) for r in rows[phase])
 train,valid=rows['training'],rows['validation'];x=np.array([r['features'] for r in train]);base=[r['actions']['baseline']['seconds'] for r in train]
 y=np.array([[r['actions'][a]['seconds']/b for a in actions] for r,b in zip(train,base)])
 fixed={}
 for group in {r['case']['topology_group'] for r in valid}:
  vv=[r for r in valid if r['case']['topology_group']==group]
  eligible=[a for a in actions if not any(r['actions'][a]['first_attempt_failures'] for r in vv)]
  fixed[group]=min(eligible,key=lambda a:sum(r['actions'][a]['seconds'] for r in vv))
 def total(m,learned):
  selected=[choose(r['case'],m,learned) for r in valid]
  return sum(r['actions'][a]['seconds'] for r,a in zip(valid,selected)),sum(r['actions'][a]['first_attempt_failures'] for r,a in zip(valid,selected)),selected
 model=dict(actions=actions,fixed=fixed,enabled=False);fixed_cost,_,_=total(model,False);trials=[];best=None
 for depth in [2,4,6]:
  for leaf in [2,4]:
   e=ExtraTreesRegressor(n_estimators=32,max_depth=depth,min_samples_leaf=leaf,random_state=31977,n_jobs=1);e.fit(x,y,sample_weight=base)
   trees=[]
   for e0 in e.estimators_:
    t=e0.tree_;trees.append(dict(left=t.children_left.tolist(),right=t.children_right.tolist(),feature=t.feature.tolist(),cut=t.threshold.tolist(),value=t.value[:,:,0].tolist()))
   for margin in [0.,.05,.1]:
    m=dict(model,enabled=True,trees=trees,margin=margin);cost,failed,selected=total(m,True);trial=dict(depth=depth,leaf=leaf,margin=margin,seconds=cost,first_attempt_failures=failed,selected=selected);trials.append(trial)
    if not failed and (best is None or cost<best[0]):best=(cost,m,trial)
 assert best is not None
 m=best[1];m['enabled']=best[0]<fixed_cost*.97;m.update(training_cases=[r['case']['id'] for r in train],validation_cases=[r['case']['id'] for r in valid],fixed_validation_seconds=fixed_cost,model_validation_seconds=best[0],validation_choice=best[2],admission='At least 3 percent validation saving over graph-specific fixed control, no failed chosen first attempts.',objective='Relative complete application cost; baseline seconds weight squared regression error; actual recovery included in each target.',source_sha256={p.name:sha(p) for p in HERE.glob('s*.py') if int(p.name[1:3])<=8})
 write(HERE/'trained_model/policy.json',m);write(HERE/'training_summary.json',dict(complete=True,training=len(train),validation=len(valid),fixed=fixed,fixed_seconds=fixed_cost,model_seconds=best[0],enabled=m['enabled'],trials=trials))
 print('trained',len(train),len(valid),'fixed',fixed_cost,'model',best[0],'enabled',m['enabled'],flush=True)
if __name__=='__main__':main()
