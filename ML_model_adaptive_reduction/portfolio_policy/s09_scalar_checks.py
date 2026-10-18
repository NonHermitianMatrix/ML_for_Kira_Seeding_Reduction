"""Check full-coordinate scalar inputs through twelve loops."""
from s00_common import *
application=module('portfolio_optimized',HERE/'s13_optimized.py')
def reduce(c,basis,reference):return application.reduce(c,basis,'application',reference)
import sympy as sp

def main():
 gen=module('scalar_full_physics',ROOT/'Kira_comparison/coverage_study/s00_cases.py');d=sp.Symbol('d');rows=[]
 for L in range(1,13):
  definition=gen.definition('propagator_massless',L,1141);n=len(definition['propagators']);p=L+1;corner=[1]*p+[0]*(n-p);ts=[corner.copy() for _ in range(3)];ts[1][0]+=1;ts[2][0]+=1;ts[2][p-1]+=2
  c=dict(id=f'full_scalar_L{L}_h1141',definition=definition,targets=ts,size=3,group=f'scalar_L{L}',topology_group='propagator_massless',split='reserved');basis=[corner];q2=sp.Rational(-2*1141-29);ref={}
  for target in ts:
   a=[1]*p;v=sp.Integer(1)
   for j in range(p):
    while a[j]<target[j]:
     A=sum(a);v*=(A-L*d/2)*(p*d/2-A-1)/((d/2-a[j]-1)*a[j]*q2);a[j]+=1
   ref[','.join(map(str,target))]={','.join(map(str,corner)):str(sp.cancel(v))}
  rp=HERE/'scalar_test'/(c['id']+'_reference.json.gz');write(rp,dict(coefficients=ref,case=c))
  tick=time.perf_counter();r=reduce(c,basis,rp);elapsed=time.perf_counter()-tick;assert r['success'] and r['reference_checked']
  write(HERE/'scalar_test'/(c['id']+'.json.gz'),r);rows.append(dict(loops=L,indices=n,seconds=elapsed,success=r['success'],coefficient_checks=r['coefficient_checks'],model_used=r['selection']['prediction_used']))
 write(HERE/'scalar_test/summary.json',dict(complete=True,rows=rows,all_exact=True,scope='Full scalar-product coordinate representation; scalar positive powers with zero auxiliary indices. Analytic identity, with no ML prediction.'))
if __name__=='__main__':main()
