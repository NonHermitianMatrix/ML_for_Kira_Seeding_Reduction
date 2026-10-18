"""Check derived one-mass formulas and canonicalize old master-index preferences."""
from s00_common import *
from s01_families import connected,products,split_blocks,gen
import s07_exact_vacuum as vacuum
EXT=HERE/'extension'

def exact_cases():
 cases=[]
 for L in range(2,14):
  c=canonical(gen.case('vacuum_one_mass',L,False,1409+6*L));P=c['definition']['physical_propagators'];N=len(c['definition']['propagators'])
  c.update(split='reserved',scope='analytic_vacuum',shape='scalar_and_one_numerator');ts=[]
  for j in [0,P-1]:
   a=[int(i<P) for i in range(N)];a[j]+=2;ts.append(a)
  if N>P:
   for j in [0,P-1]:
    a=[int(i<P) for i in range(N)];a[j]+=1;a[P]=-1;ts.append(a)
  c.update(targets=ts,size=len(ts));cases.append(c)
  if L in [3,4]:
   weighted=copy.deepcopy(c);weighted['id']+='_weighted_numerator'
   weighted['definition']['propagators'][P]['momentum']='2*k1-3*k2+k3'
   weighted['definition'].pop('quadratic_momentum_vectors',None)
   weighted['targets']=[t for t in weighted['targets'] if t[P]==-1];weighted['size']=len(weighted['targets']);cases.append(weighted)
 return cases

def exact_check():
 from s04_checks import reference,equal
 checks=[]
 for c in exact_cases():
  dest=EXT/'formula_checks'/(c['id']+'.json.gz')
  if dest.exists():checks.append(READ(dest));continue
  t=time.perf_counter();out=vacuum.reduce(c);ref=vacuum.reduce(c,reference=True)
  assert out is not None and ref is not None,c['id']
  ok,n=equal(out['coefficients'],ref['coefficients']);assert ok,(c['id'],out,ref)
  native=None;native_ok=None;native_checks=0
  if len(c['definition']['loop_momenta'])<=4:
   native=reference(c,force_native=True)
   if native['success']:
    native_ok,native_checks=equal(out['coefficients'],native['blocks'][0]['result']['coefficients']);assert native_ok,(c['id'],out,native)
  r=dict(case=c,formula=out,gamma=ref,gamma_checks=n,native=native,native_equal=native_ok,native_checks=native_checks,seconds=time.perf_counter()-t)
  write(dest,r);checks.append(r);print(json.dumps(dict(formula_case=c['id'],gamma=ok,native=native_ok,seconds=r['seconds'])),flush=True)
 write(EXT/'formula_checks/summary.json',dict(complete=True,requests=len(checks),gamma_checks=sum(r['gamma_checks'] for r in checks),native_checks=sum(r['native_checks'] for r in checks),native_verified=sum(r['native_equal'] is True for r in checks),native_unavailable=sum(r['native'] is not None and not r['native']['success'] for r in checks)))

def calibrate():
 cache=READ(HERE/'basis_cache.json');new={};rows=[];seen=set()
 # Development parameter profiles and old indices only; no reserved coefficients.
 for c0 in connected(1501,'development')+products(1507,'development'):
  if len(c0['definition']['loop_momenta'])>4:continue
  for part in split_blocks(c0):
   c=part['case'];k=key(c)
   if k in seen or k not in cache['entries']:continue
   seen.add(k);f=EXT/'basis_calibration'/(k+'.json.gz')
   if f.exists():record=READ(f)
   else:
    calibration_start=time.perf_counter();union=restore_basis(c,cache['entries'][k]['basis']);c['targets']=[list(v) for v in sorted(set(map(tuple,c['targets']+union)))];c['size']=len(c['targets'])
    attempts=[]
    for order in [1,2]:
     with rt.environment():
      os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
      r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=45,margin=0,archive=False,records=False,basis=None if order==1 else attempts[0].get('masters'),check_masters=order==2,scratch_cap=32*1024**2,bounds=inputs.bounds(c,'expanded'),ordering=order,threads=1)
     attempts.append(rt.compact(r))
     if not r['success']:break
    valid=len(attempts)==2 and all(r['success'] for r in attempts);n=0
    if valid:valid,n=equal(attempts[0]['coefficients'],attempts[1]['coefficients'])
    record=dict(case=c,success=valid,attempts=attempts,coefficient_checks=n,complete_seconds=time.perf_counter()-calibration_start);write(f,record)
   if record['success']:
    new[k]=dict(basis=store_basis(c,record['attempts'][0]['masters']),source=str(f.relative_to(ROOT)),sha256=sha(f),calibrated_all_old_indices=True)
   rows.append(dict(key=k,case=c['id'],success=record['success'],checks=record['coefficient_checks'],seconds=record['complete_seconds']));print(json.dumps(rows[-1]),flush=True)
 write(EXT/'basis_cache.json',dict(entries=new,scope='One exact master set per structure after reducing all old preferred indices on development profiles. No reserved target coefficients.'))
 write(EXT/'basis_calibration/summary.json',dict(complete=True,rows=rows,successful=len(new),complete_seconds=sum(r['seconds'] for r in rows)))

if __name__=='__main__':
 exact_check()
 import s17_massless_checks
 assert READ(EXT/'massless_formula_audit/summary.json')['complete']
 s17_massless_checks.main();calibrate()
 import s18_deployment
 s18_deployment.main()
 write(EXT/'setup_complete.json',dict(complete=True,formula_sha256=sha(HERE/'s07_exact_vacuum.py'),basis_sha256=sha(EXT/'basis_cache.json')))

if __name__=='__main__':
 from s11_extension_test import initialize
 initialize()
