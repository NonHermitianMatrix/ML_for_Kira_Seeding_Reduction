"""Shared exact arithmetic and bounded records for exceptional two-point sectors."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,math,os,random,statistics,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/tensor_reduction'
sys.path.insert(0,str(PRIOR))
from s16_rational import K,D
from s17_fast_tensor import vector
from fractions import Fraction as Q

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
from functools import lru_cache
@lru_cache(None)
def previous():
 sys.path.insert(0,str(PRIOR));m=load('lightlike_previous',PRIOR/'s18_fast_runtime.py');sys.path.insert(0,str(HERE));return m

def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,data):
 import fcntl
 p=Path(path).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(data,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  used=0
  for x in HERE.rglob('*'):
   try:
    if x.is_file():used+=x.stat().st_blocks*512
   except FileNotFoundError:pass
  assert used+len(raw)+8192<8*1024**2
  t=p.with_suffix(p.suffix+'.tmp');t.write_bytes(raw);t.replace(p)
def label(a):return ','.join(map(str,a))
