"""Bounded records and access to the frozen preceding application."""
from pathlib import Path
from functools import lru_cache
import copy,gzip,hashlib,importlib.util,json,os,sys,time,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/reconstruction_policy'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@lru_cache(None)
def prior():
 sys.path.insert(0,str(PRIOR));m=load('triangle_previous',PRIOR/'s15_deploy.py');sys.path.insert(0,str(HERE));return m
@lru_cache(None)
def helper():return prior().helper()
def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,r):
 import fcntl
 p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(r,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<2*1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())
  assert used+len(raw)+8192<20*1024**2
  tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_bytes(raw);tmp.replace(p)
def label(a):return ','.join(map(str,a))
