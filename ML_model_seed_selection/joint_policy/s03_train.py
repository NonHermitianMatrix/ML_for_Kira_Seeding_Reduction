"""Fit joint strategy costs, then freeze validation-selected choices."""
import argparse,math,statistics,time
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from s00_engine import *
from s04_cost_model import export

def candidates(g):
 protocol=rt.read(HERE/'protocols'/('pilot_'+g+'.json'))
 actions=[a for a in protocol['actions'] if a not in ['previous','native']]
 costs={a:[rt.read(HERE/'pilot'/(c['id']+'_'+a+'_r0.json.gz'))['complete_seconds'] for c in protocol['cases']] for a in actions}
 # Keep four fastest aggregate settings and the fastest setting for each pilot target.
 selected=sorted(actions,key=lambda a:sum(costs[a]))[:4]
 for i in range(len(protocol['cases'])):
  a=min(actions,key=lambda a:costs[a][i])
  if a not in selected:selected.append(a)
 return ['native']+selected

def main():
 g=sys.argv[1];actions=candidates(g)
 shapes=[(2,'single'),(3,'single'),(4,'single'),(2,'distributed'),(3,'distributed'),(4,'distributed')]
 train=[make(g,h,r,s,'training') for h in [911,912] for r,s in shapes]
 val=[make(g,h,r,s,'validation') for h in [921,922] for r,s in shapes]
 test=[make(g,h,r,s,'reserved') for h in [931,932] for r,s in shapes]
 protocol=dict(training=train,validation=val,reserved=test,actions=actions,selection='Development selects candidate configurations; validation selects model and fixed control; reserved cases remain untouched.',repetitions=5,model_gate=.02)
 save(HERE/'protocols'/(g+'.json'),protocol)
 X=[];Y=[]
 for i,c in enumerate(train):
  rows={a:evaluate(c,a,'training') for a in actions[i%len(actions):]+actions[:i%len(actions)]}
  assert all(r['success'] for r in rows.values()),c['id']
  X.append(previous.feature(c));Y.append([math.log(rows[a]['complete_seconds']/rows['native']['complete_seconds']) for a in actions])
 costs=[]
 for i,c in enumerate(val):
  rows={a:[] for a in actions}
  for rep in range(3):
   order=actions[(i+rep)%len(actions):]+actions[:(i+rep)%len(actions)]
   for a in order:rows[a].append(evaluate(c,a,'validation',rep))
  assert all(r['success'] for row in rows.values() for r in row),c['id']
  costs.append([statistics.median(r['complete_seconds'] for r in rows[a]) for a in actions])
 costs=np.array(costs);fixed=int(np.argmin(costs.sum(axis=0)));fixed_time=float(costs[:,fixed].sum())
 models=[];begin=time.perf_counter();parity=0
 for kind in ['tree','extra','forest']:
  for depth in [2,3,4]:
   if kind=='tree':m=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=1,random_state=911)
   elif kind=='extra':m=ExtraTreesRegressor(n_estimators=48,max_depth=depth,min_samples_leaf=1,random_state=911,n_jobs=1)
   else:m=RandomForestRegressor(n_estimators=48,max_depth=depth,min_samples_leaf=1,random_state=911,n_jobs=1)
   m.fit(X,Y);out=export(m)
   for c in train+val:
    assert np.max(np.abs(m.predict([previous.feature(c)])[0]-np.array(previous.predict(out,previous.feature(c)))))<1e-10;parity+=1
   for margin in [0,.03,.08]:
    choices=[]
    for c in val:
     y=previous.predict(out,previous.feature(c));j=min(range(len(y)),key=y.__getitem__)
     choices.append(j if y[j]<y[fixed]-margin else fixed)
    total=sum(costs[i,j] for i,j in enumerate(choices))
    models.append(dict(kind=kind,depth=depth,margin=margin,choices=choices,seconds=float(total),model=out))
 best=min(models,key=lambda v:v['seconds']);enabled=best['seconds']<.98*fixed_time
 # Compare validation-selected method directly to the previous complete deployment.
 old=[]
 for c in val:old.append(statistics.median(evaluate(c,'previous','validation',r)['complete_seconds'] for r in range(3)))
 selected=best['seconds'] if enabled else fixed_time;deploy=selected<.98*sum(old)
 f=dict(graph=g,actions=actions,fixed_index=fixed,enabled=enabled,deploy=deploy,signature=inputs.signature(train[0]),maximum_rank=4,minimum_rank=2,model=best['model'],margin=best['margin'],kind=best['kind'],depth=best['depth'],validation_ratio=best['seconds']/fixed_time,previous_validation_ratio=selected/sum(old),validation_choices=best['choices'],fitting_seconds=time.perf_counter()-begin,parity_checks=parity,training_cases=[c['id'] for c in train],validation_cases=[c['id'] for c in val])
 save(HERE/'trained_model'/(g+'.json'),f)
 # Fixed controls load no model weights.
 save(HERE/'trained_model'/('fixed_'+g+'.json'),{k:v for k,v in f.items() if k not in ['model','enabled','margin','kind','depth','validation_choices']})
 save(HERE/'validation'/(g+'_selection.json'),dict(costs=costs.tolist(),previous=old,models=[{k:v for k,v in x.items() if k!='model'} for x in models],fixed_index=fixed))
 save(HERE/'trained_model'/(g+'_freeze.json'),dict(complete=True,source_sha256={n:inputs.sha(HERE/n) for n in ['s00_engine.py','s03_train.py','s04_reuse.py','s05_application.py']},model_sha256=inputs.sha(HERE/'trained_model'/(g+'.json')),fixed_sha256=inputs.sha(HERE/'trained_model'/('fixed_'+g+'.json'))))
 print('FROZEN',json.dumps({k:v for k,v in f.items() if k not in ['model','signature','training_cases','validation_cases']}),flush=True)

if __name__=='__main__':main()
