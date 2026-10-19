"""Shared inputs for exact vacuum trees and measured native seed choices."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,os,statistics,sys,time,random
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/propagator_trees'
BATCH=ROOT/'ML_model_adaptive_reduction/analytic_batch'
sys.path.insert(0,str(PRIOR))
from s00_prop_common import tree,TriangleReducer
sys.path.insert(0,str(BATCH))
class LazyBatch:
 _module=None
 def __getattr__(self,name):
  if self._module is None:
   sys.path.insert(0,str(BATCH));self._module=__import__('s00_batch_common');sys.path.insert(0,str(HERE))
  return getattr(self._module,name)
batch=LazyBatch()
sys.path.insert(0,str(HERE))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
 import fcntl
 p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())+len(raw)+8192<4*1024**2
  q=p.with_suffix(p.suffix+'.tmp');q.write_bytes(raw);q.replace(p)
ACTIONS=['sparse_wide','sparse_tight','sparse_medium']
def features(c):
 x=batch.features(c);P=c['definition']['physical_propagators'];ts=c['targets']
 for j in range(P,len(ts[0])):
  vs=[-a[j] for a in ts];x.extend([min(vs),max(vs),sum(vs)/len(vs)])
 x.extend([sum(a[-1]==0 for a in ts)/len(ts),sum(a[-2]==0 for a in ts)/len(ts)])
 return x

def choose(c,method):
 if method in ACTIONS:return method,None
 if method in ['fixed','all_fixed']:return read(HERE/'trained_model/fixed.json')['action'],None
 model=read(HERE/'trained_model/policy.json')
 if not model['enabled']:return model['fixed'],None
 x=features(c)
 if any(v<a or v>b for v,a,b in zip(x,model['minimum'],model['maximum'])):return model['fixed'],None
 scores=[statistics.mean(batch.predict(t,x)[j] for t in model['trees']) for j in range(len(ACTIONS))]
 j=min(range(len(ACTIONS)),key=scores.__getitem__);k=ACTIONS.index(model['fixed'])
 if scores[j]+.002>=scores[k]*(1-model['margin']):j=k
 return ACTIONS[j],scores
