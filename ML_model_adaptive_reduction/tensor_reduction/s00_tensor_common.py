"""Shared limits and lazy access to the preceding exact and learned application."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,os,random,statistics,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/vacuum_learning'
ACTIONS=['tensor_largest','tensor_smallest','powers_largest','powers_smallest']
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
from functools import lru_cache
@lru_cache(None)
def previous():
 sys.path.insert(0,str(PRIOR));m=load('tensor_prior_application',PRIOR/'s03_runtime.py');sys.path.insert(0,str(HERE));return m
def read(path):
 p=Path(path);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
 import fcntl
 p=Path(path).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  if p.parent==HERE/'requests':used=sum(q.stat().st_blocks*512 for q in p.parent.iterdir() if q.is_file());cap=2*1024**2
  else:used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file() and q.parent!=HERE/'requests');cap=6*1024**2
  assert used+len(raw)+8192<cap,(used,len(raw),cap)
  q=p.with_suffix(p.suffix+'.tmp');q.write_bytes(raw);q.replace(p)
def label(a):return ','.join(map(str,a))
def features(c):
 ts=c['targets'];n=len(ts[0]);r=[sum(max(-v,0) for v in a) for a in ts];dots=[sum(max(v-1,0) for v in a) for a in ts];pos=[sum(v>0 for v in a) for a in ts]
 return [n,len(ts),min(r),max(r),statistics.mean(r),min(dots),max(dots),statistics.mean(dots),min(pos),max(pos),max(max(a) for a in ts),len({tuple(min(x,0) for x in a) for a in ts})]+[max(max(-a[j],0) for a in ts) if j<n else 0 for j in range(5)]+[max(max(a[j],0) for a in ts) if j<n else 0 for j in range(5)]
def predict(t,x):
 while 'feature' in t:t=t['left'] if x[t['feature']]<=t['cut'] else t['right']
 return t['cost']
def choice(c,method):
 if method in ACTIONS:return method,False
 p=HERE/'trained_model/policy.json'
 if not p.exists():return ACTIONS[0],False
 model=read(p)
 if method=='all_fixed' or not model['enabled']:return model['fixed'],False
 x=features(c)
 if any(v<a or v>b for v,a,b in zip(x,model['minimum'],model['maximum'])):return model['fixed'],False
 cost=[statistics.mean(predict(t,x)[j] for t in model['trees']) for j in range(len(ACTIONS))];j=min(range(len(ACTIONS)),key=cost.__getitem__);k=ACTIONS.index(model['fixed'])
 if cost[j]+.001>=cost[k]*(1-model['margin']):j=k
 return ACTIONS[j],True
