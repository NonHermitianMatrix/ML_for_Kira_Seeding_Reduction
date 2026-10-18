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
ACTIONS=['base','sparse_fixed','sparse_learned','raw_native']
BASE=ROOT/'ML_model_adaptive_reduction/refined_time_policy'
SPARSE=ROOT/'ML_model_seed_selection/cost_geometry'
geometry=inputs.module('hybrid_sparse_geometry',SPARSE/'s00_policy.py')
CAP=8*1024**2

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

FEATURE_NAMES=old.FEATURE_NAMES+['basis_size','basis_max_positive_sum','basis_max_rank','basis_max_dots','basis_min_lines_minus_rank','basis_rank_gap','basis_dots_gap','first_auxiliary_rank','second_auxiliary_rank']
def features(c,basis):
 x=old.features(c);basis=basis or []
 r=max([sum(max(a,0) for a in t) for t in basis] or [0]);s=max([sum(max(-a,0) for a in t) for t in basis] or [0]);d=max([sum(max(a-1,0) for a in t) for t in basis] or [0])
 tr=min([sum(a>0 for a in t)-sum(max(-a,0) for a in t) for t in basis] or [0])
 p=c['definition']['physical_propagators']
 return x+[len(basis),r,s,d,tr,max(0,s-x[7]),max(0,d-x[6])]+[max([max(0,-t[p+j]) for t in c['targets']] or [0]) if p+j<len(c['targets'][0]) else 0 for j in [0,1]]

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


def eligible(c):
 d=c['definition'];ts=c['targets']
 if len(d['loop_momenta'])!=2 or d['physical_propagators']!=7 or len(d['propagators'])!=9 or len(ts)!=1:return False
 if ts[0][:7]!=[1]*7 or not all(v<=0 for v in ts[0][7:]) or not 2<=sum(-v for v in ts[0][7:])<=4:return False
 template=canonical(inputs.case('nonplanar_box',2301,'rank2','template'))
 return inputs.signature(c)==inputs.signature(template)

def expert_feature(c):
 ts=c['targets'];x=inputs.features(c)
 for sign in [-1,1]:
  x.extend([max([max(0,sign*(t[i] if sign<0 else t[i]-1)) for t in ts] or [0]) if i<len(ts[0]) else 0 for i in range(20)])
 x.append(max(sum(v<0 for v in t) for t in ts));return x

def expert_theta(c):
 import struct
 f=READ(HERE/'trained_model/expert.json');x=[struct.unpack('f',struct.pack('f',v))[0] for v in expert_feature(c)];out=None
 for tree in f['model']['trees']:
  i=0
  while tree['left'][i]>=0:i=tree['left'][i] if x[tree['feature'][i]]<=tree['cut'][i] else tree['right'][i]
  if out is None:out=[0.]*len(tree['value'][i])
  for j,v in enumerate(tree['value'][i]):out[j]+=v/len(f['model']['trees'])
 fixed=f['fixed_index'];j=min(range(len(out)),key=out.__getitem__)
 if out[j]>=out[fixed]-f['margin']:j=fixed
 return f['candidates'][j],out
