"""Bounded study utilities and the unchanged preceding application."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,math,os,re,statistics,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PREVIOUS=ROOT/'ML_model_adaptive_reduction/fast_decomposition'
sys.path.insert(0,str(PREVIOUS))
import s12_deploy as previous
import s00_fast_common as support
read=support.read;sha=support.sha;canonical=support.canonical;label=support.label
CAP=12*1024**2
ACTIONS=['prior','sparse_wide','sparse_tight','rank_groups','single_targets']

def write(path,obj):
 import fcntl
 path=Path(path).resolve();path.relative_to(HERE);path.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode()
 if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 if path.parent!=HERE/'requests':
  with (HERE/'.storage_lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   used=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file() and p.parent!=HERE/'requests')
   assert used+len(raw)+8192<CAP-1024**2,(used,len(raw))
   q=path.with_suffix(path.suffix+'.writing');q.write_bytes(raw);q.replace(path)
 else:
  assert len(raw)<1024**2
  path.write_bytes(raw)

def legacy():return previous.candidate.legacy()

def features(c):
 ts=c['targets'];d=c['definition'];P=d['physical_propagators'];n=len(ts)
 ranks=[sum(max(-x,0) for x in a) for a in ts]
 dots=[sum(max(x-1,0) for x in a) for a in ts]
 aux=[max(-a[j],0) for a in ts for j in range(P,len(a))]
 distances=[sum(abs(a[j]-b[j]) for j in range(P,len(a))) for i,a in enumerate(ts) for b in ts[i+1:]]
 incidence=[[int(re.search(r'\b'+re.escape(k)+r'\b',p['momentum']) is not None) for k in d['loop_momenta']] for p in d['propagators'][:P]]
 structural=[sum(sum(row)>1 for row in incidence),max(sum(row[i] for row in incidence) for i in range(len(d['loop_momenta'])))]
 return [len(d['loop_momenta']),len(d['external_momenta']),len(d['propagators']),P,n,min(ranks),max(ranks),statistics.mean(ranks),len(set(ranks)),max(dots),min(sum(x>0 for x in a) for a in ts),max(aux or [0]),max(distances or [0]),statistics.mean(distances or [0]),max(sum(x<0 for x in a) for a in ts)]+structural

def eligible(c):
 d=c['definition'];x=features(c)
 return x[0]==2 and x[1]==3 and x[2]==9 and x[3]==7 and 1<=x[4]<=6 and 1<=x[5]<=x[6]<=4 and x[9]==0 and x[10]==7 and not d.get('invariants') and all(p['mass_squared']=='0' for p in d['propagators']) and all(all(v<=0 for v in a[7:]) for a in c['targets'])

def predict(tree,x):
 while 'feature' in tree:tree=tree['left'] if x[tree['feature']]<=tree['cut'] else tree['right']
 return tree['cost']

def choose(c,method):
 if method in ACTIONS:return method,None
 model=read(HERE/'trained_model/policy.json')
 if method in ['fixed','all_fixed'] or not model['enabled']:return model['fixed'],None
 x=features(c)
 if any(v<a or v>b for v,a,b in zip(x,model['minimum'],model['maximum'])):return 'prior',None
 costs=[statistics.mean(predict(t,x)[j] for t in model['trees']) for j in range(len(ACTIONS))]
 j=min(range(len(ACTIONS)),key=costs.__getitem__);k=ACTIONS.index(model['fixed'])
 if costs[j]+model['allowance']>=costs[k]*(1-model['margin']):j=k
 return ACTIONS[j],costs
