"""Check symbolic masses and exceptional sub-sectors in larger one-loop targets."""
from s00_light_common import *
from s01_lightlike import reduce as numeric
from s09_symbolic import reduce as symbolic
from s12_complete_tensor import reduce as tensor
from s11_coefficients import coefficient
from s02_cases import case

def main():
 import sympy as sp
 vac=previous().previous();h=vac.batch.legacy().h;measure=load('lightlike_extended_native',vac.BATCH/'s04_measure.py');count=0;records=[]
 for kind in ['unequal','equal','mixed']:
  c=case(101,kind,0,0,1);c['definition']['invariants']=[['x',2],['y',2]];c['definition']['propagators'][0]['mass_squared']='x';c['definition']['propagators'][1]['mass_squared']={'unequal':'y','equal':'x','mixed':'0'}[kind];c['targets']=[[a,b,0,0] for a,b in [(1,1),(2,1),(1,3),(2,2),(3,2)]];c['size']=len(c['targets']);r=symbolic(c);assert r is not None
  for x,y in [(3,7),(11,2),(17,29)]:
   cc=copy.deepcopy(c);cc['definition']['invariants']=[]
   for p in cc['definition']['propagators']:p['mass_squared']=str(sp.sympify(p['mass_squared']).subs({'x':x,'y':y}))
   rr=numeric(cc);assert rr is not None
   rows={t:{m:str(sp.cancel(sp.sympify(v).subs({'x':x,'y':y}))) for m,v in row.items()} for t,row in r['coefficients'].items()};ok,n=h.equal(rows,rr['coefficients']);assert ok,(kind,x,y);count+=n
  records.append(dict(kind=kind,case=c,result=r))
 native_checks=0
 for k,kind in enumerate(['unequal','equal','mixed']):
  c=case(111+k,kind,1,1,1);c['definition']['physical_propagators']=3;c['definition']['top_level_sectors']=[7];c['definition']['propagators'][2]['mass_squared']=str(131+k);c['targets']=[[2,1,1,-1],[1,2,1,-1],[2,1,0,-1]];c['size']=3
  r=tensor(c,'tensor_smallest',deadline=time.perf_counter()+20);assert r is not None,c['id']
  ref=measure.native(h,c,None,expanded=True);assert ref['success'],ref
  # Translation-equivalent tadpoles share one canonical coordinate.
  ms=[p['mass_squared'] for p in c['definition']['propagators']]
  def canonical(rows):
   out={}
   for t,row in rows.items():
    rr={}
    for m,v in row.items():
     a=list(map(int,m.split(',')))
     if sum(a)==1 and a.count(1)==1:
      mass=ms[a.index(1)]
      if mass=='0':continue
      z=[0]*len(a);z[ms.index(mass)]=1;m=label(z)
     rr[m]=rr.get(m,0)+sp.sympify(v)
    out[t]={m:str(sp.cancel(v)) for m,v in rr.items() if sp.cancel(v)!=0}
   return out
  ok,n=h.equal(canonical(r['coefficients']),canonical(ref['coefficients']));assert ok,(kind,'larger-sector native disagreement',r['coefficients'],ref['coefficients']);native_checks+=n
  write(HERE/'development'/('embedded_'+kind+'.json.gz'),dict(case=c,result=r,native=ref,checks=n))
 for record in records:
  for row in record['result']['coefficients'].values():
   for v in row.values():assert not sp.sympify(v).has(sp.zoo,sp.nan)
 write(HERE/'symbolic_checks.json',dict(complete=True,substitution_checks=count,embedded_native_coefficient_checks=native_checks,records=records));print(json.dumps(dict(complete=True,substitution_checks=count,embedded_native_coefficient_checks=native_checks)),flush=True)
if __name__=='__main__':main()
