"""Bounded storage and the unchanged preceding reduction application."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,os,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/analytic_batch'
CAP=8*1024**2

def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def label(a):return ','.join(map(str,a))
def write(p,obj):
 import fcntl
 p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<2*1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
  assert used+len(raw)+8192<CAP,(used,len(raw))
  q=p.with_suffix(p.suffix+'.writing');q.write_bytes(raw);q.replace(p)
def prior():
 sys.path.insert(0,str(PRIOR));import s02_batch_runtime
 return s02_batch_runtime
