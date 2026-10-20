"""Bounded study of exact reconstruction and measured-cost selection."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,gzip,fcntl
from functools import lru_cache
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TOOLS=ROOT/'.tools/kira-reconstruction'
STAGE=ROOT/'.tools/kira-reconstruction-stage'
PREVIOUS=ROOT/'ML_model_adaptive_reduction/direct_analytic'
PREVIOUS_COMMIT='93ea9e899cce3e368e38de1ac2a6699a4e9bec85'
PERSISTENT_UPPER=9_778_738_176
BUILD_LIMIT=160*1024**2
RETAINED_TOOLS_LIMIT=32*1024**2
STUDY_LIMIT=20*1024**2
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);raw=p.read_bytes()
 return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def allocated(p):
 total=0
 if Path(p).exists():
  for f in Path(p).rglob('*'):
   try:
    if f.is_file():total+=f.stat().st_blocks*512
   except FileNotFoundError:pass
 return total
def check_storage():
 n=allocated(STAGE)+allocated(TOOLS)+allocated(HERE)
 assert n<BUILD_LIMIT,n
 assert PERSISTENT_UPPER+BUILD_LIMIT<10_000_000_000
 return n
def write(p,v):
 p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(v,indent=2).encode()+b'\n'
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<2*1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert allocated(HERE)+len(raw)+8192<STUDY_LIMIT
  q=p.with_suffix(p.suffix+'.tmp');q.write_bytes(raw);q.replace(p)
def load(name,path):
 import importlib.util
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
@lru_cache(None)
def previous():
 sys.path.insert(0,str(PREVIOUS))
 m=load('reconstruction_previous',PREVIOUS/'s23_deploy.py')
 return m
@lru_cache(None)
def helper():
 return previous().helper()
