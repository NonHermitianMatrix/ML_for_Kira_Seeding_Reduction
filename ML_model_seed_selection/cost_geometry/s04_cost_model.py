"""Train a cost predictor over seed surfaces learned through native reductions."""
import argparse,copy,json,math,statistics,time
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from s03_train import FIXED,make,reference,evaluate
from s00_policy import *

def feature(c):
 ts=c['targets'];x=inputs.features(c)
 for sign in [-1,1]:
  x.extend([max([max(0,sign*(t[i] if sign<0 else t[i]-1)) for t in ts] or [0]) if i<len(ts[0]) else 0 for i in range(20)])
 x.append(max(sum(v<0 for v in t) for t in ts))
 return x

def export(m):
 ts=[m] if isinstance(m,DecisionTreeRegressor) else m.estimators_
 return dict(trees=[dict(left=t.tree_.children_left.tolist(),right=t.tree_.children_right.tolist(),feature=t.tree_.feature.tolist(),cut=t.tree_.threshold.tolist(),value=t.tree_.value[:,:,0].tolist()) for t in ts])

def predict(m,x):
 import struct
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x];out=None
 for t in m['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  if out is None:out=[0.]*len(t['value'][i])
  for j,v in enumerate(t['value'][i]):out[j]+=v/len(m['trees'])
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('graph');a=ap.parse_args();g=a.graph
 old=rt.read(HERE/'trained_model'/(g+'.json'));history=rt.read(HERE/'training'/(g+'_search.json'))['history']
 # Expand the teacher search with independent changes to the rank allowance.
 proposals=FIXED+[[1,0,0,k,b,1,0] for k,b in [(0,0),(0,1),(-1,0),(1,1.5)]]+[x['theta'] for x in sorted(history,key=lambda x:x['cost'])[:3]]
 candidates=list({json.dumps(v):v for v in proposals}.values())
 train=[make(g,h,r,s,'training') for h in [831,832] for r,s in [(2,'single'),(3,'single'),(4,'single'),(2,'distributed'),(3,'distributed'),(4,'distributed')]]
 val=[make(g,h,r,s,'validation') for h in [841,842] for r,s in [(2,'single'),(3,'single'),(4,'single'),(3,'distributed'),(4,'distributed')]]
 test=[make(g,h,r,s,'reserved') for h in [851,852] for r,s in [(2,'single'),(3,'single'),(4,'single'),(3,'distributed'),(4,'distributed')]]
 protocol=dict(training=train,validation=val,reserved=test,candidates=candidates,previous_training='protocols/'+g+'.json',objective='Predict measured log complete-time ratios for learned seed surfaces. Include model loading, prediction, exact algebra, verification, and recovery.',selection_before_test=True)
 inputs.write(HERE/'protocols'/('cost_'+g+'.json'),protocol)
 X=[];Y=[];valid_train=[]
 for c in train:
  if not reference(c)[1]['success']:continue
  rs=[evaluate(c,v,'cost_training') for v in candidates]
  if not rs[0]['success']:continue
  X.append(feature(c));Y.append([math.log((r['complete_seconds'] if r['success'] else 300)/rs[0]['complete_seconds']) for r in rs]);valid_train.append(c['id'])
 if len(X)<4:raise RuntimeError('Insufficient completed native training cases')
 costs=[];valid_val=[]
 for c in val:
  if not reference(c)[1]['success']:continue
  rows=[[evaluate(c,v,'cost_validation',rep) for rep in range(3)] for v in candidates]
  if not all(x['success'] for x in rows[0]):continue
  costs.append([statistics.median(x['complete_seconds'] if x['success'] else 300 for x in row) for row in rows]);valid_val.append(c)
 costs=np.array(costs);assert len(costs)
 fixed=int(np.argmin(costs.sum(axis=0)));models=[];start=time.perf_counter()
 for kind in ['tree','forest','extra']:
  for depth in [2,4]:
   if kind=='tree':m=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=2,random_state=831)
   elif kind=='forest':m=RandomForestRegressor(n_estimators=32,max_depth=depth,min_samples_leaf=2,random_state=831,n_jobs=1)
   else:m=ExtraTreesRegressor(n_estimators=32,max_depth=depth,min_samples_leaf=2,random_state=831,n_jobs=1)
   m.fit(X,Y);out=export(m)
   for c in valid_val:assert np.max(np.abs(m.predict([feature(c)])[0]-np.array(predict(out,feature(c)))))<1e-10
   for margin in [0,.03,.1]:
    choices=[]
    for c in valid_val:
     y=predict(out,feature(c));j=min(range(len(y)),key=y.__getitem__);choices.append(j if y[j]<y[fixed]-margin else fixed)
    total=sum(costs[i,j] for i,j in enumerate(choices));models.append(dict(kind=kind,depth=depth,margin=margin,choices=choices,seconds=float(total),model=out))
 best=min(models,key=lambda x:x['seconds']);fixed_time=float(costs[:,fixed].sum());enabled=best['seconds']<.97*fixed_time
 freeze=dict(graph=g,enabled=enabled,model=best['model'],margin=best['margin'],candidates=candidates,fixed_index=fixed,signature=inputs.signature(train[0]),maximum_rank=4,maximum_dots=0,maximum_targets=1,training_cases=valid_train,validation_cases=[c['id'] for c in valid_val],validation_choices=best['choices'],validation_ratio=best['seconds']/fixed_time,kind=best['kind'],depth=best['depth'],fitting_seconds=time.perf_counter()-start,source_sha256={n:inputs.sha(HERE/n) for n in ['s00_policy.py','s03_train.py','s04_cost_model.py']})
 inputs.write(HERE/'trained_model'/('cost_'+g+'.json'),freeze)
 inputs.write(HERE/'cost_validation'/(g+'_selection.json'),dict(cases=[c['id'] for c in valid_val],costs=costs.tolist(),models=[{k:v for k,v in z.items() if k!='model'} for z in models],fixed_index=fixed))
 print('COST_MODEL_FROZEN',json.dumps({k:v for k,v in freeze.items() if k not in ['model','signature','candidates']}),flush=True)

if __name__=='__main__':main()
