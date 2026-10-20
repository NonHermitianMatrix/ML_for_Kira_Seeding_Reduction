"""Compare exceptional tensor identities with native IBP and signed IBP residuals."""
from s00_light_common import *
from s01_lightlike import reduce
from s02_cases import case

def main():
 import sympy as sp
 old=previous().previous();h=old.batch.legacy().h;measure=load('lightlike_native_measure',old.BATCH/'s04_measure.py');rows=[];checks=0;d=sp.Symbol('d')
 for i,(kind,rank,dots) in enumerate([('unequal',0,2),('equal',0,2),('mixed',0,2),('unequal',2,1),('equal',2,1),('mixed',2,1),('massless',2,1)]):
  c=case(71+i,kind,rank,dots,2);a=reduce(c);assert a is not None,c['id']
  b=measure.native(h,c,None,expanded=True);assert b['success'],(c['id'],b)
  # Canonicalize translation-equivalent unit tadpoles in the native result.
  masses=[p['mass_squared'] for p in c['definition']['propagators']];converted={}
  for t,row in b['coefficients'].items():
   rr={}
   for m,v in row.items():
    inds=list(map(int,m.split(',')));assert sum(inds)==1 and inds.count(1)==1,(c['id'],m)
    mass=masses[inds.index(1)]
    if mass=='0':continue
    z=[0]*len(inds);z[masses.index(mass)]=1;k=label(z);rr[k]=rr.get(k,0)+sp.sympify(v)
   converted[t]={k:str(sp.cancel(v)) for k,v in rr.items() if sp.cancel(v)!=0}
  ok,n=h.equal(a['coefficients'],converted);assert ok,(c['id'],a['coefficients'],converted);checks+=n
  write(HERE/'development'/(c['id']+'.json.gz'),dict(case=c,exact=a,native=b,checks=n));rows.append(dict(case=c['id'],checks=n));print(json.dumps(rows[-1]),flush=True)
 # All denominator-index IBP vectors, including auxiliary numerator vectors.
 residuals=0
 for kind in ['unequal','equal','mixed']:
  c=case(83,kind,1,2,1);definition=c['definition'];names=['k1']+definition['external_momenta'];vs=[vector(p['momentum'],names) for p in definition['propagators']];q=[[-x*v[0] for x in v[1:]] for v in vs];ms=list(map(lambda p:Q(p['mass_squared']),definition['propagators']));rules={tuple(sorted(k)):Q(v) for k,v in definition['scalarproduct_rules']}
  def dot(a,b):return sum(Q(a[i]*b[j])*rules[tuple(sorted([names[i+1],names[j+1]]))] for i in range(3) for j in range(3))
  Y=[[ms[i]+ms[j]-dot([x-y for x,y in zip(q[i],q[j])],[x-y for x,y in zip(q[i],q[j])]) for j in range(4)] for i in range(4)]
  a=c['targets'][0]
  for i in range(4):
   terms=[(a,d-sum(a))]
   for j,v in enumerate(a):
    if not v:continue
    b=a.copy();b[j]+=1;b[i]-=1;terms.append((b,-v))
    b=a.copy();b[j]+=1;terms.append((b,-v*Y[i][j]))
   cc=dict(c,targets=[t for t,_ in terms]);r=reduce(cc);assert r is not None
   total={}
   for t,f in terms:
    for m,v in r['coefficients'][label(t)].items():total[m]=total.get(m,0)+f*sp.sympify(v)
   assert all(sp.cancel(v)==0 for v in total.values()),(kind,i,total)
   residuals+=len(total)
 write(HERE/'checks.json',dict(complete=True,native_coefficient_checks=checks,ibp_residual_coefficients=residuals,pilot=rows))
 print('All exact checks passed.',flush=True)
if __name__=='__main__':main()
