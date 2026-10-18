"""Construct and split integral families with independent loop-momentum blocks."""
from s00_common import *
gen=module('thirteen_physical_families',ROOT/'Kira_comparison/coverage_study/s00_cases.py')

def connected(h,split):
 out=[]
 for L in range(1,14):
  for kind in ['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive','ladder','bubble_box']:
   if L==1 and kind in ['vacuum_all_mass','bubble_box']:continue
   c=gen.case(kind,L,False,h);d=c['definition'];P=d['physical_propagators'];N=len(d['propagators'])
   c['targets']=[]
   for j in range(min(P,3)):
    a=[int(i<P) for i in range(N)];a[(h+j)%P]+=2 if L%2 else 1
    if not L%2 and N>P:a[P+(h+j)%(N-P)]=-1
    c['targets'].append(a)
   c.update(split=split,size=len(c['targets']),shape='dots' if L%2 else 'mixed',scope='coupled_family',topology_group=kind+'_L'+str(L));out.append(canonical(c))
 for kind in ['nonplanar_box','pentagon','one_mass_box']:
  c=inputs.case(kind,h,'mixed',split);c['scope']='coupled_family';out.append(canonical(c))
 return out

def compose(blocks,name,split):
 # Blocks share external kinematics. Their loop variables are distinct.
 blocks=[canonical(c) for c in blocks];first=blocks[0]['definition'];E=len(first['external_momenta'])
 assert all(c['definition']['external_momenta']==first['external_momenta'] and c['definition']['scalarproduct_rules']==first['scalarproduct_rules'] for c in blocks)
 physical=[];aux=[];maps=[];groups=[];offset=0
 for c in blocks:
  d=c['definition'];lm=d['loop_momenta'];rename={n:'k'+str(offset+i+1) for i,n in enumerate(lm)}
  props=[dict(p,momentum=replace_names(p['momentum'],rename)) for p in d['propagators']]
  P=d['physical_propagators'];maps.append((len(physical),len(aux),P,len(props)-P))
  physical+=props[:P];aux+=props[P:];groups.append(list(range(offset,offset+len(lm))));offset+=len(lm)
 P=len(physical);props=physical+aux
 for i,g in enumerate(groups):
  for h in groups[i+1:]:
   props.extend(dict(momentum='k'+str(a+1)+'-k'+str(b+1),mass_squared='0') for a in g for b in h)
 N=len(props);assert N==offset*(offset+1)//2+offset*E
 targets=[]
 for j in range(3):
  a=[0]*N
  for c,(ps,ns,p,n) in zip(blocks,maps):
   t=c['targets'][j%len(c['targets'])];a[ps:ps+p]=t[:p];a[P+ns:P+ns+n]=t[p:]
  if a not in targets:targets.append(a)
 d=dict(loop_momenta=['k'+str(i+1) for i in range(offset)],external_momenta=first['external_momenta'],propagators=props,physical_propagators=P,top_level_sectors=[(1<<P)-1],scalarproduct_rules=first['scalarproduct_rules'],invariants=first.get('invariants',[]),parameters=dict(profile=first.get('parameters',{}).get('profile')),rank=N)
 return dict(id=name,group=name,topology_group=name.split('_L')[0],split=split,definition=d,targets=targets,size=len(targets),scope='independent_loop_blocks',shape='block_products')

def products(h,split):
 out=[]
 for L in range(1,14):
  profile=h+4*L
  for kind in ['vacuum_all_mass','propagator_massive','ladder','nonplanar_box']:
   blocks=[];left=L
   while left:
    size=min(2,left)
    if kind=='nonplanar_box':
     c=inputs.case('nonplanar_box' if size==2 else 'one_mass_box',profile,'dots',split)
     # A one-loop remainder must use the same external invariants as the box.
     if blocks:c['definition']['scalarproduct_rules']=copy.deepcopy(blocks[0]['definition']['scalarproduct_rules'])
    else:
     c=gen.case(kind,size,False,profile)
     P=c['definition']['physical_propagators'];N=len(c['definition']['propagators'])
     c['targets']=[]
     for j in range(min(3,P)):
      a=[int(i<P) for i in range(N)];a[(profile+j)%P]+=1+(j==1);c['targets'].append(a)
     c['size']=len(c['targets'])
    blocks.append(c);left-=size
   out.append(compose(blocks,'product_'+kind+'_L'+str(L)+'_h'+str(profile),split))
 return out

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

def initialize():
 if (HERE/'protocol.json').exists():
  old=READ(HERE/'protocol.json')
  if old.get('product_profile_rule')=='1307+4*L' and old.get('cache_version')==3:return
  assert not list((HERE/'coverage').glob('*.json')) and not list((HERE/'model_test').glob('*.json.gz'))
  write(HERE/'protocol_initial_unmeasured.json.gz',old)
 cases=connected(1301,'reserved')+products(1307,'reserved')
 # Use union bases from all previously checked target sets, not the smallest set.
 entries={};sources=[]
 for base in [general.HERE,general.HERE/'refit']:
  for c in READ(base/'protocol.json')['reserved']:
   f=base/'references'/(c['id']+'.json.gz');check=f.with_name(c['id']+'_check.json.gz')
   coverage=base/'coverage'/(c['id']+'.json')
   if not coverage.exists() or READ(coverage)['status']!='verified':continue
   if not f.exists() or not check.exists():continue
   r=READ(f);k=key(c);entry=entries.setdefault(k,dict(basis=[],sources=[]))
   entry['basis']=sorted(set(map(tuple,entry['basis']))|set(map(tuple,store_basis(c,r['masters']))))
   entry['sources'].append(dict(path=str(f.relative_to(ROOT)),sha256=sha(f),check_sha256=sha(check)))
 for folder in ['preparation','recovery']:
  base=general.HERE/folder
  for c in READ(base/'protocol.json')['cases']:
   f=base/'model_test'/(c['id']+'_cached_native_r0.json.gz')
   if not f.exists():continue
   r=READ(f)
   if not r.get('success') or r.get('status')!='verified' or not r.get('coefficient_checks'):continue
   entry=entries.setdefault(key(c),dict(basis=[],sources=[]))
   entry['basis']=sorted(set(map(tuple,entry['basis']))|set(map(tuple,store_basis(c,r['masters']))))
   entry['sources'].append(dict(path=str(f.relative_to(ROOT)),sha256=sha(f),independent_coefficient_checks=r['coefficient_checks']))
 write(HERE/'basis_cache.json',dict(entries=entries,scope='Union of checked earlier master-index sets. Coefficients are always recomputed. Cache construction predates this experiment.'))
 write(HERE/'protocol.json',dict(cases=cases,repetitions=3,profiles=[1301,1307],product_profile_rule='1307+4*L',cache_version=3,methods=['native','fixed','learned','previous'],loops=list(range(1,14)),complete_timeout_seconds=110,native_call_timeout_seconds=45,source_commit='6bb73048f95a4ef3b6fcea1a1e39bdcbfa0c730a',scope='Finite coupled and exactly factorable families through thirteen loops. General irreducible high-loop reductions remain subject to native representation and resource limits.'))
 print(json.dumps(dict(cases=len(cases),cached_structures=len(entries))),flush=True)

if __name__=='__main__':initialize()
