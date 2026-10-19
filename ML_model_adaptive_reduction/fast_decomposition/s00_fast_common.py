"""Small shared utilities; import the historical Kira application only on demand."""
from pathlib import Path
import json,gzip,hashlib,importlib.util,os,sys,time,copy,re,math,statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'ML_model_adaptive_reduction/analytic_decomposition'
CAP=12*1024**2

def read(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def legacy():
 sys.path.insert(0,str(PRIOR));m=module('fast_prior_runtime',PRIOR/'s10_runtime.py');sys.path.insert(0,str(HERE));return m

def write(p,obj):
 import fcntl
 p=Path(p).resolve();p.relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(obj,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 if p.parent==HERE/'requests':
  assert len(raw)<(256*1024 if p.suffix=='.json' else 3*1024**2)
  q=p.with_suffix(p.suffix+'.writing');q.write_bytes(raw);q.replace(p);return
 ledger=HERE/'.storage_bytes'
 with (HERE/'.storage_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  try:used=int(ledger.read_text())
  except (FileNotFoundError,ValueError):used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file() and not q.name.startswith('.') and q.parent!=HERE/'requests')
  prior=p.stat().st_blocks*512 if p.exists() else 0
  assert used+((len(raw)+4095)//4096)*4096+8192<CAP-2*1024**2
  ledger.write_text('dirty');q=p.with_suffix(p.suffix+'.writing');q.write_bytes(raw);n=q.stat().st_blocks*512;q.replace(p);ledger.write_text(str(used-prior+n))

def label(a):return ','.join(map(str,a))
def canonical(c):
 c=copy.deepcopy(c);d=c['definition'];lm=d['loop_momenta'];em=d['external_momenta'];mapping={n:'k'+str(i+1) for i,n in enumerate(lm)}|{n:'p'+str(i+1) for i,n in enumerate(em)}
 def replace(t):return re.sub(r'\b[A-Za-z_]\w*\b',lambda m:mapping.get(m[0],m[0]),str(t))
 for p in d['propagators']:p['momentum']=replace(p['momentum'])
 d['loop_momenta']=[mapping[n] for n in lm];d['external_momenta']=[mapping[n] for n in em];d['scalarproduct_rules']=[[[mapping[n] for n in pair],v] for pair,v in d['scalarproduct_rules']]
 return c

def basis(c):
 c=canonical(c);d=c['definition'];P=d['physical_propagators'];perm=sorted(range(P),key=lambda i:(d['propagators'][i]['momentum'],d['propagators'][i]['mass_squared']=='0'))+sorted(range(P,len(d['propagators'])),key=lambda i:(d['propagators'][i]['momentum'],d['propagators'][i]['mass_squared']=='0'))
 props=[d['propagators'][i] for i in perm];sectors=sorted(sum(1<<i for i,j in enumerate(perm) if s&(1<<j)) for s in d['top_level_sectors'])
 s=json.dumps(dict(loops=d['loop_momenta'],external=d['external_momenta'],propagators=[(p['momentum'],p['mass_squared']=='0') for p in props],physical=P,sectors=sectors,invariants=d.get('invariants',[]),products=[(a,v=='0') for a,v in d['scalarproduct_rules']]),sort_keys=True);key=hashlib.sha256(s.encode()).hexdigest()
 bs=read(PRIOR/'basis_registry.json').get(key)
 if bs is None:bs=read(ROOT/'ML_model_adaptive_reduction/factorized_policy/extension/basis_cache.json')['entries'].get(key)
 if bs is None:return None
 inv=[perm.index(j) for j in range(len(perm))];return [[a[j] for j in inv] for a in bs['basis']]

def admit(c,r):
 allowed=basis(c)
 if allowed is None:return None
 labels={label(a) for a in allowed};mapping={};props=c['definition']['propagators']
 for m in r['masters']:
  k=label(m)
  if k in labels:mapping[k]=k;continue
  active=[i for i,v in enumerate(m) if v]
  if len(active)==1 and m[active[0]]==1:
   mass=props[active[0]]['mass_squared'];replacement=next((label(a) for a in allowed if sum(a)==1 and all(x in [0,1] for x in a) and props[a.index(1)]['mass_squared']==mass),None)
   if replacement is not None:mapping[k]=replacement;continue
  return None
 rows={}
 for t,row in r['coefficients'].items():
  out={}
  for m,v in row.items():
   k=mapping[m];out[k]='('+out[k]+')+('+v+')' if k in out else v
  rows[t]=out
 r.update(coefficients=rows,masters=allowed);return r

def split_blocks(case):
 c=canonical(case);d=c['definition'];lm=d['loop_momenta'];N=len(d['propagators'])
 if d.get('cut_propagators') or d.get('symbolic_ibp'):raise ValueError('Unsupported cut or symbolic-index family')
 inc=[{i for i,k in enumerate(lm) if re.search(r'\b'+re.escape(k)+r'\b',p['momentum'])} for p in d['propagators']]
 parent=list(range(len(lm)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for j,group in enumerate(inc):
  if any(t[j]!=0 for t in c['targets']):
   if not group:raise ValueError('Active loop-independent factor needs separate handling')
   first=min(group)
   for i in group:parent[find(i)]=find(first)
 groups={}
 for i in range(len(lm)):groups.setdefault(find(i),set()).add(i)
 parts=[];coverage=set()
 for group in sorted(groups.values(),key=min):
  indices=[j for j,s in enumerate(inc) if s and s<=group]
  physical=[j for j in indices if j<d['physical_propagators']]
  auxiliary=[j for j in indices if j>=d['physical_propagators']];indices=physical+auxiliary
  expected=len(group)*(len(group)+1)//2+len(group)*len(d['external_momenta'])
  if len(indices)!=expected:raise ValueError('The selected scalar-product coordinates do not form a complete block')
  sd=copy.deepcopy(d);sd['loop_momenta']=[lm[i] for i in sorted(group)];sd['propagators']=[d['propagators'][j] for j in indices];sd['physical_propagators']=len(physical);sd['top_level_sectors']=[(1<<len(physical))-1];sd['rank']=len(indices)
  sd.pop('quadratic_momentum_vectors',None)
  ts=list(dict.fromkeys(tuple(t[j] for j in indices) for t in c['targets']))
  part=canonical(dict(c,id=c['id']+'_block'+str(len(parts)),definition=sd,targets=[list(t) for t in ts],size=len(ts)))
  parts.append(dict(case=part,indices=indices,loops=sorted(group)))
  coverage.update(indices)
 assert all(t[j]==0 for t in c['targets'] for j in range(N) if j not in coverage)
 return parts

