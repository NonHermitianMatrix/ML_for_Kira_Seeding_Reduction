"""Bounded storage and the preceding learned reduction application."""
from pathlib import Path
import sys,json,gzip,hashlib,os,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PREVIOUS=ROOT/'ML_model_adaptive_reduction/hybrid_experts'
sys.path.insert(0,str(PREVIOUS))
import s00_cost_common as h
previous=h.inputs.module('analytic_previous_runtime',PREVIOUS/'s01_runtime.py')
from s00_recurrence import reduce as recurrence
READ=h.READ

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
 p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 if p.parent==HERE/'requests':
  assert len(raw)<(256*1024 if p.suffix=='.json' else 3*1024**2)
  temp=p.with_suffix(p.suffix+'.writing');temp.write_bytes(raw);temp.replace(p);return
 import fcntl
 ledger=HERE/'.storage_bytes'
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  try:used=int(ledger.read_text())
  except (FileNotFoundError,ValueError):used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file() and q.name not in ['.storage_lock','.storage_bytes'] and q.parent!=HERE/'requests')
  previous=p.stat().st_blocks*512 if p.exists() else 0
  assert used+((len(raw)+4095)//4096)*4096+8192<10*1024**2
  ledger.write_text('dirty\n');temp=p.with_suffix(p.suffix+'.writing');temp.write_bytes(raw);actual=temp.stat().st_blocks*512;temp.replace(p);ledger.write_text(str(used-previous+actual)+'\n')

def signature(c):return h.key(c)
def basis(c):
 p=HERE/'basis_registry.json';registry=READ(p) if p.exists() else {}
 entry=registry.get(signature(c))
 return h.restore_basis(c,entry['basis']) if entry else h.basis_for(c,READ(h.BLOCK/'extension/basis_cache.json'))

def exact(c):
 old=h.exact(c)
 if old is not None:return old
 r=recurrence(c,deadline=time.perf_counter()+5)
 if r is None:return None
 allowed=basis(c)
 if allowed is None:return None
 allowed_labels={h.label(m) for m in allowed};props=c['definition']['propagators'];mapping={}
 for m in r['masters']:
  label=h.label(m)
  if label in allowed_labels:mapping[label]=label;continue
  active=[i for i,a in enumerate(m) if a]
  if len(active)==1 and m[active[0]]==1:
   mass=props[active[0]]['mass_squared']
   replacement=next((h.label(a) for a in allowed if sum(a)==1 and all(x in [0,1] for x in a) and props[a.index(1)]['mass_squared']==mass),None)
   if replacement is not None:mapping[label]=replacement;continue
  return None
 rows={}
 for t,row in r['coefficients'].items():
  out={}
  for m,x in row.items():
   key=mapping[m];out[key]='('+out[key]+')+('+x+')' if key in out else x
  rows[t]=out
 r['coefficients']=rows;r['masters']=allowed;r['basis_description']='Supplied independently checked Kira master indices.'
 return r

# Historical modules extend sys.path; restore this application for local imports.
sys.path.insert(0,str(HERE))
