"""Check exact formulas and compare recurrence pivot actions before training."""
from s00_fast_common import *
from s01_fast_recurrence import reduce as recurrence
from s02_fast_formulas import reduce as formulas
from s03_fast_runtime import run

def main():
 old=legacy();h=old.h
 poly=h.inputs.module('fast_polygon_cases',PRIOR/'s03_cases.py').polygon
 checks=[]
 for L in [1,2,4,8,13]:
  for kind in ['vacuum_one_mass','propagator_massless']:
   c=h.canonical(h.gen.case(kind,L,False,2601));r=formulas(c);ref=h.exact(c)
   assert r is not None and ref is not None,(L,kind)
   ok,n=h.equal(r['coefficients'],ref['coefficients']);assert ok,(L,kind)
   checks.append(dict(L=L,kind=kind,checks=n))
 rows=[]
 for n in [3,4,5]:
  for a in [[3]+[1]*(n-1),[2,2]+[1]*(n-2),[3,3]+[1]*(n-2),[1]*(n-2)+[3,3]]:
   c=poly(n,2601,1);c.update(targets=[a],size=1)
   reference=h.recurrence(c) if hasattr(h,'recurrence') else old.recurrence(c)
   costs={}
   for action in ['largest','smallest','first','last']:
    t=time.perf_counter();r=recurrence(c,pivot=action,backend='gmp',deadline=time.perf_counter()+10);elapsed=time.perf_counter()-t
    assert r is not None
    ok,k=h.equal(r['coefficients'],reference['coefficients']);assert ok,(n,a,action)
    costs[action]=dict(seconds=elapsed,states=r['recurrence_states'])
   rows.append(dict(n=n,target=a,costs=costs));print(json.dumps(rows[-1]),flush=True)
 write(HERE/'pilot.json',dict(complete=True,formula_checks=checks,pivot_costs=rows))
if __name__=='__main__':main()
