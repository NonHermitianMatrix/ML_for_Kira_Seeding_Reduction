"""Learn action cost and failure risk from completed and failed exact attempts."""
from s00_common import *
import s02_application as shared
import struct
P=HERE/'preparation'

def predict(m,x):
 # This model has cost and failure outputs; the seed model has ten outputs.
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x]
 out=[0.]*len(m['trees'][0]['value'][0])
 for t in m['trees']:
  i=0
  while t['left'][i]>=0:
   i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  for j,v in enumerate(t['value'][i]):out[j]+=v/len(m['trees'])
 return out

def excluded(c):
 return len(c['definition']['loop_momenta'])>=6 or any(k in c.get('topology_group','') for k in ['vacuum_all_mass','nonplanar','pentagon'])

def vector(c,bounds,trunc,basis_count,has_basis,ordering):
 return features(c)+list(bounds)+[int(trunc is not None),float(trunc or 0),int(has_basis),basis_count,ordering]

def choose(c,basis):
 f=READ(P/'trained_model/freeze.json');items=[]
 for a in (ACTIONS if basis is not None else ['native','rank_plus','expanded','truncate','truncate_rank_plus','truncate_relaxed']):
  x=vector(c,inputs.bounds(c,a),inputs.truncation(c,a),len(basis or []),basis is not None,1)
  logt,risk=predict(f['model'],x);p=min(1.,max(0.,risk/3));score=math.exp(min(8,max(-5,logt)))+f['penalty_seconds']*p
  items.append(dict(action=a,score=score,failure_score=p))
 return min(items,key=lambda v:v['score'])['action']

def train():
 import numpy as np
 from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor
 from s01_train import export
 rows=[];sources=[];validation=[]
 def add(c,r,source):
  if excluded(c) or 'seed_bounds' not in r or 'complete_seconds' not in r:return
  prescribed=r.get('prescribed_basis');has_basis=prescribed is not None
  # Native records retain the input basis as a list, if one was supplied.
  count=len(prescribed) if isinstance(prescribed,list) else (len(r.get('masters',[])) if has_basis else 0)
  x=vector(c,r['seed_bounds'],r.get('truncate_sp'),count,has_basis,r.get('integral_ordering',1))
  rows.append((x,[math.log(max(.001,r['complete_seconds'])),3*float(not r['success'])]));sources.append(source)
 # Existing training only, plus the completed initial implementation trial.
 for folder in ['learned_seed_bounds','portfolio_policy']:
  root=ROOT/'ML_model_adaptive_reduction'/folder
  for c in READ(root/'protocol.json')['splits']['training']:
   if excluded(c):continue
   for a in ACTIONS:
    f=root/'training'/(c['id']+'_'+a+('_r0' if folder=='portfolio_policy' else '')+'.json.gz')
    if not f.exists():continue
    r=READ(f)
    for rr in r.get('attempts',[]):add(c,rr,str(f.relative_to(ROOT)))
 for c in READ(HERE/'protocol.json')['reserved']:
  if excluded(c):continue
  for suffix in ['', '_check']:
   f=HERE/'references'/(c['id']+suffix+'.json.gz')
   if f.exists():add(c,READ(f),str(f.relative_to(ROOT)))
  for m in ['native','fixed','learned']:
   f=HERE/'model_test'/(c['id']+'_'+m+'_r0.json.gz')
   if f.exists():
    for r in READ(f).get('attempts',[]):add(c,r,str(f.relative_to(ROOT)))
 # Model selection uses older validation requests, never the fresh profile 1237.
 for folder in ['learned_seed_bounds','portfolio_policy']:
  root=ROOT/'ML_model_adaptive_reduction'/folder
  for c in READ(root/'protocol.json')['splits']['validation']:
   if excluded(c):continue
   choices=[]
   for a in ACTIONS:
    f=root/'validation'/(c['id']+'_'+a+('_r0' if folder=='portfolio_policy' else '')+'.json.gz')
    if not f.exists():continue
    r=READ(f);ats=r.get('attempts',[])
    if not ats:continue
    q=ats[0];prescribed=q.get('prescribed_basis');bc=len(prescribed) if isinstance(prescribed,list) else len(q.get('masters',[]))
    choices.append(dict(action=a,x=vector(c,q['seed_bounds'],q.get('truncate_sp'),bc,True,1),cost=r['complete_seconds'] if r['success'] else 180.,failed=not q['success']))
   if len(choices)==len(ACTIONS):validation.append(choices)
 assert rows and validation
 X=np.array([a for a,b in rows]);Y=np.array([b for a,b in rows]);best=None;options=[];start=time.perf_counter()
 for kind in ['extra','forest']:
  for depth in [4,6]:
   m=(ExtraTreesRegressor if kind=='extra' else RandomForestRegressor)(n_estimators=32,max_depth=depth,min_samples_leaf=5,n_jobs=1,random_state=1231)
   m.fit(X,Y);f=export(m,kind,np.zeros(X.shape[1]),np.ones(X.shape[1]))
   for penalty in [0.,20.,60.,120.]:
    total=base=0.;failed=0
    for choices in validation:
     pred=m.predict([v['x'] for v in choices]);scores=np.exp(np.clip(pred[:,0],-5,8))+penalty*np.clip(pred[:,1]/3,0,1);i=int(scores.argmin());total+=choices[i]['cost'];base+=choices[0]['cost'];failed+=choices[i]['failed']
    score=(total+60*failed)/base;v=dict(kind=kind,depth=depth,penalty_seconds=penalty,cost_ratio=total/base,first_failures=failed,score=score);options.append(v)
    if best is None or score<best['selection']['score']:
     best=dict(model=f,selection=v,penalty_seconds=penalty);best_estimator=m
 # Check the exported implementation on all training inputs.
 for x,y in zip(X,best_estimator.predict(X)):assert np.max(np.abs(np.array(predict(best['model'],x))-y))<1e-8
 best.update(complete=True,training_attempts=len(rows),failed_training_attempts=int(sum(y[1]>0 for _,y in rows)),validation_requests=len(validation),features=FEATURE_NAMES+['bound_r','bound_s','bound_d','truncated','truncation_level','basis_available','basis_count','integral_ordering'],fitting_seconds=time.perf_counter()-start,options=options,sources=sources,scope='Historical training plus initial profile 1201 attempts. Selection uses historical validation only. Exclude the distinct-mass vacuum family, nonplanar boxes, pentagons, and loops six and above. Profile 1237 remains fresh.')
 write(P/'trained_model/freeze.json',best);write(P/'trained_model/selection.json',{k:v for k,v in best.items() if k not in ['model','sources','options']})
 from s14_prepare import initialize
 initialize();print(json.dumps(best['selection']),flush=True)
if __name__=='__main__':train()
