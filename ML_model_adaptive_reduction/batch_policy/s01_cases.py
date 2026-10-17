"""Build target batches and independently checked references from native IBP systems."""
import copy,json,time,hashlib
from s00_runtime import HERE,ROOT,FILTER,rt,inputs,save,attempt,partition
GRAPHS=['sunrise','double_box','vacuum3','ladder3','nonplanar_box','pentagon','one_mass_box','bubble_box3','massless4','bubble_box4']
PATTERNS=['dots','rank','mixed','dots_rank','pinched_rank','all']

def case(g,h,pattern,split):
 simple=g in ['bubble_box3','bubble_box4','massless4'];shapes=['dot','numerator','corner'] if simple else ['dots','rank2','mixed','pinched']
 atoms={s:inputs.case(g,h,s,split) for s in shapes}
 names={'dots':[shapes[0]],'rank':[shapes[1]],'mixed':[shapes[2]],'dots_rank':shapes[:2],'pinched_rank':[shapes[-1],shapes[1]],'all':shapes}[pattern]
 c=copy.deepcopy(atoms[names[0]]);ts=[]
 for s in names:
  for a in atoms[s]['targets']:
   if a not in ts:ts.append(a)
 c.update(id=f'{g}_h{h}_batch_{pattern}',shape=pattern,targets=ts,size=len(ts),components=[atoms[s] for s in names]);return c

def make(h,split,graphs=GRAPHS):
 out=[];seen=set()
 for g in graphs:
  for p in PATTERNS:
   c=case(g,h,p,split);key=(g,tuple(sorted(map(tuple,c['targets']))))
   if key in seen:continue
   seen.add(key);out.append(c)
 return out

def initialize():
 f=rt.read(FILTER/'trained_model/freeze.json');cfg=dict(seed_actions=f['seed_config']['fixed_by_graph'],signatures={g:d['signatures'] for g,d in f['features'].items()},filter_hashes={n[:-4]:h for p,h in f['models'].items() for n in [p.split('/')[-1]]},source_freeze_sha256=inputs.sha(FILTER/'trained_model/freeze.json'))
 p=HERE/'fixed_inputs.json'
 if p.exists():assert rt.read(p)==cfg
 else:inputs.write(p,cfg)

def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if p.exists():return p if rt.read(p)['success'] else None
 basis=[];sources=[]
 for atom in c['components']:
  q=HERE/'references'/(atom['id']+'_discovery.json.gz')
  if q.exists():r=rt.read(q)
  else:r=attempt(atom,None,'expanded',timeout=90);save(q,rt.compact(r))
  sources.append(str(q.relative_to(HERE)))
  if not r['success']:
   save(p,dict(case=c['id'],success=False,reason='Component master discovery exceeded common limits.',sources=sources));return None
  for a in r['masters']:
   if a not in basis:basis.append(a)
 coeff={};checks=[]
 for atom in c['components']:
  key=hashlib.sha256(json.dumps(basis,sort_keys=True).encode()).hexdigest()[:16]
  cached=HERE/'references'/(atom['id']+'_basis_'+key+'.json.gz')
  if cached.exists():
   previous=rt.read(cached);assert previous['masters']==basis
   if previous['success']:
    coeff.update(previous['coefficients']);checks.append(dict(cache=str(cached.relative_to(HERE)),sha256=inputs.sha(cached)));continue
   save(p,dict(case=c['id'],success=False,reason='Cached common-basis check failed.',sources=sources,check=str(cached.relative_to(HERE))));return None
  r=attempt(atom,basis,'expanded',timeout=90)
  if not r['success']:
   save(p,dict(case=c['id'],success=False,reason='Common-basis component reduction failed.',sources=sources,attempt=rt.compact(r)));return None
  temp=HERE/'references'/(c['id']+'_component_check.json.gz');save(temp,rt.compact(r))
  bounds=inputs.bounds(atom,'expanded');bounds[1]+=1
  larger=attempt(atom,basis,'expanded',timeout=90,custom=bounds);rt.verify(larger,temp);temp.unlink();checks.append(rt.compact(larger))
  save(cached,dict(success=larger['success'],masters=basis,coefficients=r['coefficients'],check=rt.compact(larger)))
  if not larger['success']:
   save(p,dict(case=c['id'],success=False,reason='Enlarged component check failed.',sources=sources,checks=checks));return None
  for a,row in r['coefficients'].items():
   if a in coeff and row!=coeff[a]:raise ValueError('Component reference disagreement')
   coeff[a]=row
 save(p,dict(case=c['id'],success=True,masters=basis,coefficients=coeff,sources=sources,checks=checks,reference_checked=True));return p

if __name__=='__main__':initialize()
