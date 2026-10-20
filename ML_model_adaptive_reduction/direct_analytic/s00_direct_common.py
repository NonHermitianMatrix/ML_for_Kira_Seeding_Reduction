"""Shared bounded records and lazy access to the published workflow."""
from pathlib import Path
import copy,gzip,importlib.util,json,math,os,random,statistics,sys,time
from functools import lru_cache
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/lightlike_reduction'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@lru_cache(None)
def current():
 sys.path.insert(0,str(PRIOR));m=load('direct_previous',PRIOR/'s05_runtime.py');sys.path.insert(0,str(HERE));return m
@lru_cache(None)
def helper():return current().previous().previous().batch.legacy().h
@lru_cache(None)
def reference_module():
 path=ROOT/'ML_model_adaptive_reduction/analytic_batch';sys.path.insert(0,str(path));m=load('direct_reference',path/'s04_measure.py');sys.path.insert(0,str(HERE));return m

def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(path,data):
 import fcntl
 p=Path(path).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(data,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<2*1024**2
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);used=0
  for x in HERE.rglob('*'):
   try:
    if x.is_file():used+=x.stat().st_blocks*512
   except FileNotFoundError:pass
  assert used+len(raw)+8192<12*1024**2
  t=p.with_suffix(p.suffix+'.tmp');t.write_bytes(raw);t.replace(p)
def label(a):return ','.join(map(str,a))
