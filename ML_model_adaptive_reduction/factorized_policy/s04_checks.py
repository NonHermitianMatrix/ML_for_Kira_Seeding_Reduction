"""Check factorization, scalar formulas, and native block reductions."""
from s00_common import *
from s01_families import split_blocks,products,connected,gen
from s03_runtime import formula,run,run_block

def gamma_reference(c):
 import sympy as sp
 d=c['definition'];L=len(d['loop_momenta']);P=d['physical_propagators'];N=len(d['propagators']);dim=sp.Symbol('d')
 assert P==L+1 and len(d['external_momenta'])==1 and all(p['mass_squared']=='0' for p in d['propagators'])
 p2=sp.sympify(d['scalarproduct_rules'][0][1],rational=True);basis=label([1]*P+[0]*(N-P));rows={}
 for a in c['targets']:
  assert all(v>=1 for v in a[:P]) and not any(a[P:]);delta=sum(a[:P])-P
  value=sp.rf(P-L*dim/2,delta)*sp.rf(P*dim/2-P-delta,delta)/p2**delta
  for v in a[:P]:value/=sp.rf(dim/2-v,v-1)*sp.factorial(v-1)
  rows[label(a)]={basis:str(sp.cancel(value))}
 return dict(success=True,coefficients=rows,masters=[list(map(int,basis.split(',')))],route='independent_gamma_ratio')

def reference(c,timeout=45,force_native=False):
 """Independent validation data; runtime never receives its coefficients."""
 parts=split_blocks(c);out=[];cache=READ(HERE/'basis_cache.json');memo={}
 for part in parts:
  sub=part['case'];f=formula(sub)
  signature=json.dumps([sub['definition']['loop_momenta'],sub['definition']['external_momenta'],sub['definition']['propagators'],sub['definition']['scalarproduct_rules'],sub['targets']],sort_keys=True)
  if signature in memo:
   out.append(dict(indices=part['indices'],case=sub,result=memo[signature],reused=True));continue
  if f is not None and f['route']=='massless_scalar_recurrence' and not force_native:
   ref=gamma_reference(sub);ok,n=equal(f['coefficients'],ref['coefficients']);assert ok
   memo[signature]=ref;out.append(dict(indices=part['indices'],case=sub,result=ref));continue
  if len(sub['definition']['propagators'])>31:return dict(success=False,status='unsupported_native_index_count',blocks=out)
  entry=cache['entries'].get(key(sub));basis=restore_basis(sub,entry['basis']) if entry else ([[1]] if f is not None else None)
  trials=[]
  for action in ['expanded','native']:
   with rt.environment():
    os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
    r=rt.native.run(sub,sub['size'],'native',HERE/'unused',timeout=timeout,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=inputs.bounds(sub,action),ordering=2,threads=1)
   r=rt.compact(r);trials.append(r)
   if r['success']:break
  r=dict(r,reference_attempts=trials);memo[signature]=r;out.append(dict(indices=part['indices'],case=sub,result=r))
  if not r['success']:return dict(success=False,status=r['status'],blocks=out)
 return dict(success=True,status='reference_completed',blocks=out)

def compare(result,ref):
 if not result.get('success') or not ref.get('success'):return False,0
 if len(result['blocks'])!=len(ref['blocks']):return False,0
 checks=0
 for a,b in zip(result['blocks'],ref['blocks']):
  if a['indices']!=b['indices']:return False,checks
  ok,n=equal(a['result']['coefficients'],b['result']['coefficients']);checks+=n
  if not ok:return False,checks
 return True,checks

def expand_small(c,result):
 import itertools,sympy as sp
 N=len(c['definition']['propagators']);rows={}
 for t in c['targets']:
  choices=[]
  for b in result['blocks']:
   local=label([t[j] for j in b['indices']]);choices.append(list(b['result']['coefficients'][local].items()))
  assert math.prod(len(v) for v in choices)<=256
  row={}
  for combination in itertools.product(*choices):
   a=[0]*N;value=sp.Integer(1)
   for b,(master,coefficient) in zip(result['blocks'],combination):
    for j,v in zip(b['indices'],map(int,master.split(','))):a[j]=v
    value*=sp.sympify(coefficient.replace('^','**'),rational=True)
   key=label(a);row[key]=str(sp.cancel(sp.sympify(row.get(key,'0'))+value))
  rows[label(t)]=row
 return rows

def main():
 from s01_families import initialize
 assert READ(HERE/'trained_model/freeze.json')['complete']
 initialize()
 observations=[]
 # Each constructed high-loop product must split into complete local coordinates.
 cases=products(1297,'development')
 for c in cases:
  parts=split_blocks(c);assert sum(len(p['case']['definition']['loop_momenta']) for p in parts)==len(c['definition']['loop_momenta'])
  assert all(len(p['case']['definition']['propagators'])<=31 for p in parts)
 # An active cross-block numerator must merge the affected loop blocks.
 c=copy.deepcopy(next(c for c in cases if c['id'].startswith('product_vacuum_all_mass_L2_')))
 # L2 construction is one two-loop block; use four loops for the cross check.
 c=copy.deepcopy(next(c for c in cases if c['id'].startswith('product_vacuum_all_mass_L4_')))
 before=split_blocks(c);c['targets'][0][-1]=-1;after=split_blocks(c);assert len(before)==2 and len(after)==1
 # New exact tadpole and independent gamma representations agree with native Kira.
 for kind in ['vacuum_all_mass','propagator_massless']:
  c=canonical(gen.case(kind,1,False,1297));c['split']='development'
  c['targets']=[[a]+([1] if kind.startswith('propagator') else []) for a in [2,3,4]];c['size']=3
  ref=reference(c,force_native=True);out=run(c,'native');ok,n=compare(out,ref);assert ok,(kind,out,ref)
  if kind=='propagator_massless':assert equal(out['blocks'][0]['result']['coefficients'],gamma_reference(c)['coefficients'])[0]
  observations.append(dict(case=c['id'],checks=n,success=ok))
 # Compare a true product reduction with a monolithic native Kira calculation.
 a=canonical(gen.case('vacuum_all_mass',1,False,1297));a['split']='development'
 from s01_families import compose
 c=compose([a,a],'pilot_independent_vacua_L2','development');out=run(c,'learned');assert out['success'];want=expand_small(c,out)
 masters=[list(map(int,k.split(','))) for k in sorted({m for row in want.values() for m in row})]
 with rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  native=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=45,margin=0,archive=False,records=False,basis=masters,check_masters=True,scratch_cap=32*1024**2,bounds=inputs.bounds(c,'expanded'),ordering=2,threads=1)
 assert native['success'];ok,n=equal(want,native['coefficients']);assert ok
 write(HERE/'checks/monolithic_product.json.gz',dict(case=c,product=out,native=rt.compact(native),coefficient_checks=n))
 observations.append(dict(case=c['id'],checks=n,success=ok))
 # One actual learned block call, checked against independent coefficients.
 c=next(c for c in cases if c['id'].startswith('product_ladder_L2_'))
 ref=reference(c);out=run(c,'learned');ok,n=compare(out,ref);assert ok,(out,ref)
 write(HERE/'checks/learned_block.json.gz',dict(case=c,reference=ref,result=out,coefficient_checks=n))
 observations.append(dict(case=c['id'],checks=n,success=ok))
 write(HERE/'checks/summary.json',dict(complete=True,structural_product_cases=len(cases),cross_block_numerator_merges=True,rows=observations,source_sha256={p.name:sha(p) for p in HERE.glob('s0[0-4]*.py')},model_sha256=sha(HERE/'trained_model/freeze.json'),cache_sha256=sha(HERE/'basis_cache.json')))
 print(json.dumps(dict(complete=True,checks=observations)),flush=True)

if __name__=='__main__':main()
