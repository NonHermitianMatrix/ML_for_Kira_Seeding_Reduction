"""Shared definitions for exact block reduction and learned seed costs."""
import copy,gzip,hashlib,importlib.util,json,math,os,re,statistics,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/general_policy'))
import s00_common as general
# Loaded by path under a distinct name when this file is the current s00_common.
if not hasattr(general,'FEATURE_NAMES'):
 spec=importlib.util.spec_from_file_location('historical_general_common',ROOT/'ML_model_adaptive_reduction/general_policy/s00_common.py')
 general=importlib.util.module_from_spec(spec);spec.loader.exec_module(general)
inputs=general.inputs;rt=general.rt;ACTIONS=general.ACTIONS;READ=general.READ
features=general.features;FEATURE_NAMES=general.FEATURE_NAMES
CAP=32*1024**2
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(d,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<4*1024**2
 assert sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())+len(raw)+8192<CAP
 q=p.with_name(p.name+'.writing');q.write_bytes(raw);q.replace(p)
def module(name,p):return inputs.module(name,p)
def replace_names(text,mapping):
 return re.sub(r'\b[A-Za-z_]\w*\b',lambda m:mapping.get(m[0],m[0]),str(text))
def canonical(case):
 c=copy.deepcopy(case);d=c['definition'];lm=d['loop_momenta'];em=d['external_momenta']
 mapping={n:'k'+str(i+1) for i,n in enumerate(lm)}|{n:'p'+str(i+1) for i,n in enumerate(em)}
 for p in d['propagators']:p['momentum']=replace_names(p['momentum'],mapping)
 d['loop_momenta']=[mapping[n] for n in lm];d['external_momenta']=[mapping[n] for n in em]
 d['scalarproduct_rules']=[[[mapping[n] for n in pair],v] for pair,v in d['scalarproduct_rules']]
 return c
def coordinates(c):
 d=canonical(c)['definition'];P=d['physical_propagators']
 def order(j):
  p=d['propagators'][j];return p['momentum'],p['mass_squared']=='0'
 return sorted(range(P),key=order)+sorted(range(P,len(d['propagators'])),key=order)
def key(c):
 c=canonical(c);d=c['definition'];perm=coordinates(c)
 d['propagators']=[d['propagators'][j] for j in perm]
 d['top_level_sectors']=sorted(sum(1<<i for i,j in enumerate(perm) if s&(1<<j)) for s in d['top_level_sectors'])
 return hashlib.sha256(inputs.signature(c).encode()).hexdigest()
def store_basis(c,basis):
 perm=coordinates(c);return [[a[j] for j in perm] for a in basis]
def restore_basis(c,basis):
 perm=coordinates(c);inverse=[perm.index(j) for j in range(len(perm))]
 return [[a[j] for j in inverse] for a in basis]
def label(a):return ','.join(map(str,a))
def nontrivial(result):return any(row and row!={t:'1'} for t,row in result.get('coefficients',{}).items())
def equal(a,b):
 if set(a)!=set(b):return False,0
 checks=0
 for t,row in a.items():
  for m in set(row)|set(b[t]):
   x,y=row.get(m,'0'),b[t].get(m,'0');checks+=1
   if x!=y:
    import sympy as sp
    if sp.cancel(sp.sympify(x.replace('^','**'),rational=True)-sp.sympify(y.replace('^','**'),rational=True))!=0:return False,checks
 return True,checks
