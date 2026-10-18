"""Shared paths, limits, and physical features for complete-time selection."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BLOCK=ROOT/'ML_model_adaptive_reduction/factorized_policy'
sys.path.insert(0,str(BLOCK))
import s00_common as old
from s00_common import (copy,gzip,hashlib,json,math,os,re,statistics,time,READ,sha,canonical,key,restore_basis,label,equal,inputs,rt,nontrivial)
from s01_families import split_blocks,connected,products,gen
from s03_runtime import formula
import s07_exact_vacuum as vacuum
import s16_massless_tensor as tensor
from s04_checks import compare
ACTIONS=['native','rank_plus','expanded','truncate','truncate_rank_plus','truncate_relaxed','raw_native']
CAP=16*1024**2

def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(d,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
 assert used+len(raw)+8192<CAP,(used,len(raw))
 q=p.with_name(p.name+'.writing');q.write_bytes(raw);q.replace(p)

def exact(c):
 r=vacuum.reduce(c)
 if r is None:r=tensor.reduce(c)
 return formula(c) if r is None else r

def basis_for(c,cache):
 e=cache['entries'].get(key(c));return restore_basis(c,e['basis']) if e else None

FEATURE_NAMES=old.FEATURE_NAMES+['basis_size','basis_max_positive_sum','basis_max_rank','basis_max_dots','basis_min_lines_minus_rank','basis_rank_gap','basis_dots_gap']
def features(c,basis):
 x=old.features(c);basis=basis or []
 r=max([sum(max(a,0) for a in t) for t in basis] or [0]);s=max([sum(max(-a,0) for a in t) for t in basis] or [0]);d=max([sum(max(a-1,0) for a in t) for t in basis] or [0])
 tr=min([sum(a>0 for a in t)-sum(max(-a,0) for a in t) for t in basis] or [0])
 return x+[len(basis),r,s,d,tr,max(0,s-x[7]),max(0,d-x[6])]

def settings(c,a,basis):
 if a=='raw_native':return inputs.bounds(c,'native'),None
 b=inputs.bounds(c,a);tr=inputs.truncation(c,a)
 if basis:
  # Include the requested basis in the seeding bounds and truncation region.
  b=[max(b[j],max(sum(max(v-(1 if j==2 else 0),0) if j!=1 else max(-v,0) for v in t) for t in basis)) for j in range(3)]
  if tr is not None:tr=min(tr,min(sum(v>0 for v in t)-sum(max(-v,0) for v in t) for t in basis))
 return b,tr
