"""Check the closed coefficient formula against native IBP and independent gamma ratios."""
import gzip,json,random,statistics,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/batch_policy'))
from s00_runtime import inputs,rt
from s00_formula import reduce,coefficient,domain
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);raw=gzip.compress(json.dumps(d,separators=(',',':')).encode(),mtime=0)
 assert sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())+len(raw)+4096<2*1024**2;p.write_bytes(raw)
def make(L,h,symbolic=False):
 gen=inputs.module('banana_physical_cases',ROOT/'Kira_comparison/coverage_study/s00_cases.py');d=gen.definition('propagator_massless',L,h,symbolic);n=L+1;N=len(d['propagators']);a=[1]*n+[0]*(N-n);ts=[]
 for k in range(3):
  t=a.copy();t[(h+k)%n]+=1+(k==2)
  if t not in ts:ts.append(t)
 return dict(id=f'banana_L{L}_h{h}_'+('symbolic' if symbolic else 'rational'),group=f'banana_L{L}',topology_group='massless_banana',split='independent_formula_test',definition=d,targets=ts,size=len(ts))
def verify(r,want):
 import sympy as sp
 assert set(r['coefficients'])==set(want['coefficients']);checks=0
 for a,row in want['coefficients'].items():
  for m in set(row)|set(r['coefficients'][a]):
   x=r['coefficients'][a].get(m,'0');y=row.get(m,'0');assert sp.cancel(sp.sympify(x.replace('^','**'),rational=True)-sp.sympify(y.replace('^','**'),rational=True))==0;(checks:=checks+1)
 return checks
def main():
 import sympy as sp,mpmath as mp
 native_cases=[make(L,811,False) for L in range(1,7)]+[make(L,812,True) for L in range(1,5)]
 protocol=dict(native_cases=native_cases,repetitions=3,formula_loop_orders=list(range(1,13))+[16,24,32],dimension_points=['257/101','401/97'],native_bounds='Target positive and extra powers, rank zero; known corner master.',native_timeout_seconds=90,binary_sha256=inputs.sha(rt.BINARY),formula_sha256=inputs.sha(HERE/'s00_formula.py'))
 p=HERE/'model_test/protocol.json'
 if p.exists():assert rt.read(p)==protocol
 else:inputs.write(p,protocol)
 checked=[]
 for c in native_cases:
  basis=[domain(c)['master']]
  for j in range(3):
   q=HERE/'model_test'/(c['id']+f'_r{j}.json.gz')
   if q.exists():continue
   tick=time.perf_counter();r=rt.attempt(c,basis,action='native',timeout=90);native_seconds=time.perf_counter()-tick
   fast=reduce(c,basis);exact=False;checks=0
   if r['success']:
    check_start=time.perf_counter();checks=verify(r,fast);native_seconds+=time.perf_counter()-check_start;exact=True
   timed=[]
   # Formula times include domain checks and an exact reference comparison.
   if exact:
    for rep in range(3):
     tick=time.perf_counter();out=reduce(c,basis);verify(out,r);timed.append(time.perf_counter()-tick)
   save(q,dict(case=c['id'],success=r['success'],native_seconds=native_seconds,native=rt.compact(r),formula=fast,formula_checked_seconds=timed,exact=exact,checks=checks))
   print('NATIVE_FORMULA',c['id'],j,r['success'],native_seconds,timed,flush=True)
   if not r['success']:break
 # Independent high-loop checks use uncancelled gamma functions at noninteger dimensions.
 mp.mp.dps=70;records=[];rng=random.Random(811)
 for L in protocol['formula_loop_orders']:
  n=L+1
  for k in range(8):
   a=[1]*n
   for j in range(1+k):a[rng.randrange(n)]+=1
   text=coefficient(L,a,'-1651');expr=sp.sympify(text,rational=True)
   for dim in protocol['dimension_points']:
    dv=sp.Rational(dim);dd=mp.mpf(str(dv.p))/int(dv.q);A=sum(a);K=A-n
    value=mp.gamma(A-L*dd/2)/mp.gamma(n-L*dd/2)*mp.gamma(n*dd/2-n)/mp.gamma(n*dd/2-A)
    for ai in a:value*=mp.gamma(dd/2-ai)/(mp.gamma(dd/2-1)*mp.factorial(ai-1))
    value*=mp.mpf(-1651)**(-K)
    got=mp.mpf(str(sp.N(expr.subs({'d':dv}),65)));error=abs(got-value)/max(mp.mpf(1),abs(value));assert error<mp.mpf('1e-55')
    records.append(dict(loops=L,powers=a,dimension=dim,relative_error=str(error),coefficient=text))
 save(HERE/'model_test/gamma_checks.json.gz',dict(passed=True,checks=len(records),records=records))
 rows=[];failed=[];checks=0
 for c in native_cases:
  rs=[rt.read(q) for j in range(3) if (q:=HERE/'model_test'/(c['id']+f'_r{j}.json.gz')).exists()]
  checks+=sum(r['checks'] for r in rs)
  if len(rs)!=3 or not all(r['success'] and r['exact'] for r in rs):failed.append(c['id']);continue
  native=statistics.median(r['native_seconds'] for r in rs);fast=statistics.median(t for r in rs for t in r['formula_checked_seconds'])
  rows.append(dict(case=c['id'],loops=len(c['definition']['loop_momenta']),symbolic=bool(c['definition']['invariants']),native_seconds=native,formula_checked_seconds=fast,speedup=native/fast))
 out=dict(complete=True,matched=rows,failed=failed,native_coefficient_checks=checks,gamma_checks=len(records),formula_loop_orders=protocol['formula_loop_orders'],learned_gain=False,all_successful_native_outputs_exact=True,binary_sha256=protocol['binary_sha256'],formula_sha256=protocol['formula_sha256'])
 inputs.write(HERE/'summary.json',out);inputs.write(ROOT/'report/massless_banana_data.json',out);print('BANANA_SUMMARY',json.dumps(out),flush=True)
if __name__=='__main__':main()
