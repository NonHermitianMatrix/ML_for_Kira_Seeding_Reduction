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
ACTIONS=['native','rank_plus','expanded','truncate','truncate_rank_plus','truncate_relaxed','raw_native','checked_truncate','checked_truncate_rank']
CAP=16*1024**2

def allocation_change(p,raw=None):
 """Account shared output allocation under a lock; recover by scanning after a crash."""
 import fcntl
 p=Path(p).resolve();p.relative_to(HERE)
 p.parent.mkdir(parents=True,exist_ok=True)
 # Request files and application outputs have a separate 16 MiB transient
 # reserve for two workers. This also covers outputs from the prior runtime,
 # which does not use this writer. Keep them outside the persistent ledger.
 if p.parent==HERE/'requests':
  if raw is None:p.unlink(missing_ok=True);return
  assert len(raw)<(256*1024 if p.suffix=='.json' else 3*1024**2)
  temporary=p.with_name(p.name+'.writing');temporary.write_bytes(raw);temporary.replace(p);return
 ledger=HERE/'.storage_bytes';lock=HERE/'.storage_lock'
 with lock.open('a') as handle:
  fcntl.flock(handle,fcntl.LOCK_EX)
  try:used=int(ledger.read_text())
  except (FileNotFoundError,ValueError):
   used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file() and q not in [ledger,lock] and q.parent!=HERE/'requests')
  previous=p.stat().st_blocks*512 if p.exists() else 0
  if raw is None:
   ledger.write_text('dirty\n');p.unlink(missing_ok=True);ledger.write_text(str(used-previous)+'\n');return
  temporary=p.with_name(p.name+'.writing')
  stale=temporary.stat().st_blocks*512 if temporary.exists() else 0
  # Leave 2 MiB for guides, logs, and edits outside this writer, and retain
  # space for both the old and new file during replacement.
  bound=((len(raw)+4095)//4096)*4096
  assert used+bound+8192<CAP-2*1024**2,(used,bound)
  ledger.write_text('dirty\n')
  temporary.write_bytes(raw);actual=temporary.stat().st_blocks*512
  temporary.replace(p);ledger.write_text(str(used-previous-stale+actual)+'\n')

def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(d,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 allocation_change(p,raw)

def remove(p):allocation_change(p)

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
 checked=a in ['checked_truncate','checked_truncate_rank']
 original={'checked_truncate':'truncate','checked_truncate_rank':'truncate_rank_plus'}.get(a,a)
 b=inputs.bounds(c,original);tr=inputs.truncation(c,original)
 if basis:
  b=[max(b[j],max(sum(max(v-(1 if j==2 else 0),0) if j!=1 else max(-v,0) for v in t) for t in basis)) for j in range(3)]
  if tr is not None:
   if checked:
    limits=[]
    for m in basis:
     rank=sum(max(-v,0) for v in m);sector=sum(1<<i for i,v in enumerate(m) if v>0)
     explicit=b[1] if sector in c['definition']['top_level_sectors'] else 0
     if rank>max(1,explicit):limits.append(sum(v>0 for v in m)+1-rank)
    tr=min([tr]+limits)
   else:tr=min(tr,min(sum(v>0 for v in m)-sum(max(-v,0) for v in m) for m in basis))
 return b,tr
