"""Bounded files and access to the frozen preceding application."""
from pathlib import Path
import importlib.util,json,gzip,sys,os,time,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PREVIOUS=ROOT/'ML_model_adaptive_reduction/gamma_cancellation'
TREE=ROOT/'ML_model_adaptive_reduction/loop_coverage13'
sys.path.insert(0,str(PREVIOUS))
from s00_gamma_common import tree
from s01_gamma_cancellation import Reducer as TriangleReducer
sys.path.insert(0,str(HERE))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def previous():return load('prop_previous_runtime',PREVIOUS/'s02_runtime.py')
def read(p):
    p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
    p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(obj,separators=(',',':')).encode()
    if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    assert len(raw)<3*1024**2
    assert sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())+len(raw)<6*1024**2
    p.write_bytes(raw)
