"""Independent partial-fraction, radial-integral, and native tadpole checks."""
from s00_direct_common import *
from s05_vacuum import poles,decompose
import sympy as sp

def sympy_reference(c):
 from s05_vacuum import factors
 match=factors(c)
 if match is None:return None
 ids,masses=match;z,d=sp.symbols('z d');blocks=[];memo={}
 for i,js in enumerate(ids):
  cc=copy.deepcopy(c);cc['definition']['loop_momenta']=['k1'];cc['definition']['propagators']=[dict(c['definition']['propagators'][j],momentum='k1') for j in js];cc['targets']=[list(t) for t in dict.fromkeys(tuple(t[j] for j in js) for t in c['targets'])];ms=[masses[j] for j in js];key=(tuple(ms),tuple(map(tuple,cc['targets'])))
  if key not in memo:
   rows={};identities=0
   for a in cc['targets']:
    f=sp.prod((z-sp.Rational(m.numerator,m.denominator))**(-n) for m,n in zip(ms,a));apart=sp.apart(f,z);assert sp.cancel(f-apart)==0;row={}
    for term in sp.Add.make_args(apart):
     num,den=sp.fraction(term);roots=sp.roots(den,z)
     if not roots:continue
     assert len(roots)==1
     x,r=next(iter(roots.items()));v=sp.cancel(term*(z-x)**r);assert not v.has(z)
     if x:
      master=[0]*len(ms);master[ms.index(Q(str(x)))]=1;k=label(master);ratio=v*sp.prod(d/2-j for j in range(1,r))/(sp.factorial(r-1)*x**(r-1));row[k]=row.get(k,0)+ratio
    rows[label(a)]={k:str(sp.cancel(v)) for k,v in row.items() if sp.cancel(v)!=0};identities+=1
   memo[key]=dict(success=True,status='completed',coefficients=rows,masters=[list(map(int,m.split(','))) for m in sorted({m for row in rows.values() for m in row})],rational_identity_checks=identities)
  blocks.append(dict(indices=js,case=cc,result=memo[key]))
 return dict(success=True,blocks=blocks)

def main():
 from s07_exact_cases import vacuum
 rng=random.Random(23417);z,d=sp.symbols('z d');identities=0;coefficients=0
 for i in range(48):
  ms=[Q(rng.choice([0,2,3,5])) for _ in range(rng.randint(1,5))];a=[rng.randint(-2,3) for _ in ms]
  f=sp.prod((z-sp.Rational(m.numerator,m.denominator))**(-n) for m,n in zip(ms,a));pp=poles(ms,a);proper=sum((sp.Rational(v.numerator,v.denominator)/(z-sp.Rational(x.numerator,x.denominator))**r for (x,r),v in pp.items()),sp.Integer(0));rem=sp.cancel(f-proper);assert sp.denom(rem)==1 or not sp.denom(rem).has(z);identities+=1
 for L in [1,2,7,13]:
  c=vacuum(L,23431+L,True);a=decompose(c);b=sympy_reference(c);ok,n=helper().compare(a,b);assert ok,(L,'independent partial fractions');coefficients+=n
 # A convergent Euclidean radial integral independently checks the normalization.
 import mpmath as mp
 mp.mp.dps=35;numerical=[]
 for dd in [mp.mpf('1.3'),mp.mpf('2.7')]:
  masses=[mp.mpf(2),mp.mpf(5)];powers=[2,2];A=sum(powers);rho=dd/2
  quadrature=mp.quad(lambda t:t**(rho-1)/mp.fprod((t+x)**a for x,a in zip(masses,powers)),[0,1,mp.inf])/mp.gamma(rho)
  pp=poles([Q(2),Q(5)],powers);analytic=mp.mpf(0)
  for (x,r),v in pp.items():analytic+=mp.mpf(v.numerator)/v.denominator*(-1)**(A+r)*mp.gamma(r-rho)/mp.gamma(r)*mp.mpf(x.numerator/x.denominator)**(rho-r)
  relative=abs(analytic-quadrature)/abs(quadrature);assert relative<mp.mpf('1e-20');numerical.append(dict(d=str(dd),relative_error=str(relative)))
 # Native IBP checks the independently defined single-mass recurrence.
 c=vacuum(1,23459);c['definition']['propagators']=c['definition']['propagators'][:1];c['definition'].update(physical_propagators=1,top_level_sectors=[1],rank=1);c['targets']=[[1],[2],[3],[4]];c['size']=4
 ref=reference_module().native(helper(),c,[[1]],expanded=True);assert ref['success'];actual=decompose(c)['blocks'][0]['result'];ok,n=helper().equal(actual['coefficients'],ref['coefficients']);assert ok
 # Check the scaleless rule against native IBP and reject a massive near miss.
 from s07_exact_cases import massless_vacuum
 from s05_vacuum import scaleless
 zero_checks=0
 for L in [1,2]:
  cc=massless_vacuum(L);rr=scaleless(cc);native=reference_module().native(helper(),cc,None,expanded=True);assert native['success'];assert set(rr['coefficients'])==set(native['coefficients']);ok,k=helper().equal(rr['coefficients'],native['coefficients']);assert ok;zero_checks+=k
  bad=copy.deepcopy(cc);bad['definition']['propagators'][0]['mass_squared']='1';assert scaleless(bad) is None
 write(HERE/'checks.json',dict(complete=True,random_rational_identities=identities,independent_coefficient_checks=coefficients,native_tadpole_coefficient_checks=n,native_scaleless_coefficient_checks=zero_checks,native_scaleless_target_checks=6,convergent_radial_integrals=numerical));print('exact checks complete',flush=True)
if __name__=='__main__':main()
