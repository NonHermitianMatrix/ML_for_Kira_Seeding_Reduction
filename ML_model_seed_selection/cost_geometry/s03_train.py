"""Fit sparse seed boundaries by evolutionary search on complete exact cost."""
import argparse,copy,hashlib,json,math,random,statistics,time
from s00_policy import *

FIXED=[None,[1,0,0,1,0,1,0],[2,0,0,1,0,1,0]]

def make(g,h,rank,shape,split):
 c=inputs.case(g,h,'rank'+str(rank),split)
 c['targets']=c['targets'][:1];c['size']=1;c['shape']=shape+str(rank)
 n=len(c['targets'][0]);p=c['definition']['physical_propagators']
 if shape=='distributed' and n-p>=2:
  a=c['targets'][0];a[p:]=[0]*(n-p);i=(h+1)%(n-p);j=(i+1)%(n-p)
  a[p+i]=-((rank+1)//2);a[p+j]=-(rank//2)
 c['id']=g+'_h'+str(h)+'_'+shape+str(rank)
 return c

def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if not p.exists():
  attempts=[]
  for a in dict.fromkeys([action(c),'expanded']):
   r=rt.attempt(c,None,a,timeout=90);attempts.append(rt.compact(r))
   if r['success']:break
  r['discovery_attempts']=attempts;save(p,rt.compact(r))
 return p,rt.read(p)

def evaluate(c,theta,phase,repetition=0):
 h=hashlib.sha256(json.dumps(theta).encode()).hexdigest()[:12]
 out=HERE/phase/(c['id']+'_'+h+'_r'+str(repetition)+'.json.gz')
 if out.exists():return rt.read(out)
 refp,ref=reference(c)
 if not ref['success']:
  r=dict(case=c['id'],success=False,reference_failure=True,complete_seconds=300,theta=theta)
 else:
  try:r=run(c,ref['masters'],theta,refp,timeout=60)
  except ValueError as e:r=dict(case=c['id'],success=False,complete_seconds=300,error=str(e))
 r['theta']=theta;save(out,r)
 print(json.dumps(dict(phase=phase,case=c['id'],theta=theta,success=r['success'],seconds=r['complete_seconds'],fallbacks=r.get('fallbacks'))),flush=True)
 return r

def main():
 parser=argparse.ArgumentParser();parser.add_argument('graph');a=parser.parse_args();g=a.graph
 rng=random.Random(803+sum(map(ord,g)))
 # Different index positions and separate kinematics in each split.
 train=[make(g,811,2,'single','training'),make(g,812,4,'single','training'),make(g,811,4,'distributed','training')]
 val=[make(g,813,2,'single','validation'),make(g,814,4,'single','validation'),make(g,813,4,'distributed','validation')]
 test=[make(g,h,rank,shape,'reserved') for h in [821,822] for rank,shape in [(3,'single'),(4,'single'),(3,'distributed'),(4,'distributed')]]
 protocol=dict(training=train,validation=val,reserved=test,objective='Mean log complete-time ratio to tuned native Kira; includes all failed attempts, recovery, and exact checks.',optimizer='Elite Gaussian search over seven seed-boundary parameters.',seed=803+sum(map(ord,g)),fixed_controls=FIXED)
 inputs.write(HERE/'protocols'/(g+'.json'),protocol)
 # Read training references only. Preserve failed definitions.
 train=[c for c in train if reference(c)[1]['success']]
 if not train:
  inputs.write(HERE/'trained_model'/(g+'.json'),dict(enabled=False,reason='No completed training references'));return
 baseline={c['id']:evaluate(c,None,'training')['complete_seconds'] for c in train}
 history=[];seen=set();mean=[1.5,0,0,1,.4,1,-.15];sigma=[.7,.3,.3,.7,.4,.3,.3]
 for generation in range(3):
  proposals=([x for x in FIXED[1:]]+[[1.5,0,0,1,0,1,-.25],[2,0,0,1,1,1,-.25]]) if generation==0 else []
  while len(proposals)<8:
   v=[round(rng.gauss(m,s)*4)/4 for m,s in zip(mean,sigma)]
   v=[min(3,max(0,v[0])),min(1,max(-1,v[1])),min(1,max(-1,v[2])),min(2,max(-1,v[3])),min(2,max(0,v[4])),1,min(.5,max(-1,v[6]))]
   if tuple(v) not in seen and v not in proposals:proposals.append(v)
  for theta in proposals:
   if tuple(theta) in seen:continue
   seen.add(tuple(theta));rows=[evaluate(c,theta,'training') for c in train]
   cost=statistics.mean(math.log(max(.001,r['complete_seconds'])/baseline[c['id']]) if r['success'] else math.log(300/baseline[c['id']]) for c,r in zip(train,rows))
   history.append(dict(theta=theta,cost=cost,generation=generation,failures=sum(not r['success'] for r in rows),fallbacks=sum(r.get('fallbacks',0) for r in rows)))
  elite=sorted(history,key=lambda x:x['cost'])[:4]
  mean=[statistics.mean(x['theta'][j] for x in elite) for j in range(7)]
  sigma=[max(.2,statistics.pstdev(x['theta'][j] for x in elite)) for j in range(7)]
  inputs.write(HERE/'training'/(g+'_search.json'),dict(history=history,mean=mean,sigma=sigma,generation=generation))
 candidates=FIXED+[x['theta'] for x in sorted(history,key=lambda x:x['cost'])[:3]]
 candidates=list({json.dumps(x):x for x in candidates}.values());scores=[]
 for theta in candidates:
  rows=[evaluate(c,theta,'validation',rep) for c in val for rep in range(3)]
  usable=[c for c in val if not next(r for r in rows if r['case']==c['id']).get('reference_failure')]
  total=sum(statistics.median(r['complete_seconds'] for r in rows if r['case']==c['id']) for c in usable)
  if not usable or any(not r['success'] for r in rows if not r.get('reference_failure')):total=1e9
  scores.append(dict(theta=theta,seconds=total,fallbacks=sum(r.get('fallbacks',0) for r in rows),usable=len(usable)))
 best=min(scores,key=lambda x:x['seconds']);fixed=min([x for x in scores if x['theta'] in FIXED],key=lambda x:x['seconds'])
 # Keep an actual learned improvement over separately tuned fixed tube controls.
 enabled=best['seconds']<.97*fixed['seconds'] and best['theta'] not in FIXED and best['fallbacks']==0
 freeze=dict(graph=g,enabled=enabled,theta=best['theta'] if enabled else None,fixed_theta=fixed['theta'],best_training=sorted(history,key=lambda x:x['cost'])[0],validation=scores,training_count=len(train),signature=inputs.signature(train[0]),max_rank=4,source_sha256={n:inputs.sha(HERE/n) for n in ['s00_policy.py','s03_train.py']},gate=.03)
 inputs.write(HERE/'trained_model'/(g+'.json'),freeze)
 print('FROZEN',json.dumps(freeze),flush=True)

if __name__=='__main__':main()
