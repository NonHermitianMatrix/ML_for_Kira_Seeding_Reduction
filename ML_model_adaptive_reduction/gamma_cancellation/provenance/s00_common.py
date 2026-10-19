"""Load the frozen connected-integral implementation without changing it."""
from pathlib import Path
import importlib.util,json,sys,time,hashlib,gzip,os
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'ML_model_adaptive_reduction/loop_coverage13'
sys.path.insert(0,str(BASE))
import s01_bubble_tree as tree
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def read(p):
    p=Path(p)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(p,obj):
    p=Path(p);p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(obj,separators=(',',':')).encode()
    if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    assert len(raw)<2*1024**2
    assert sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())+len(raw)<4*1024**2
    p.write_bytes(raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
