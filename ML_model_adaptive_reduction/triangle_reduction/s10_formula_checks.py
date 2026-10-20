"""Check the derived coefficients, exact recurrences, and rejection conditions."""
from s00_triangle_common import *
from s02_triangle_cases import triangle,triangle_cases
from s01_triangle import reduce,coefficient,recognize
from fractions import Fraction as Q

def main():
 import sympy as sp
 import mpmath as mp
 mp.mp.dps=70;d=sp.Symbol('d');checks=0;maximum=mp.mpf(0)
 for a in range(1,5):
  for b in range(5):
   for c in range(1,5):
    A=a+b+c
    if A>8:continue
    rational=sp.sympify(str(coefficient(a,b,c,Q(17))),locals={'d':d})
    for dim in [mp.mpf(7)/3,mp.mpf(23)/5]:
     h=dim/2
     gamma=(-1)**A*mp.mpf(17)**(2-A)*mp.gamma(A-h)*mp.gamma(h-a-b)*mp.gamma(h-b-c)*mp.gamma(dim-2)/(mp.gamma(2-h)*mp.gamma(h-1)**2*mp.gamma(dim-A)*mp.factorial(a-1)*mp.factorial(c-1))
     direct=mp.mpf(str(sp.N(rational.subs(d,sp.Rational(7,3) if dim<3 else sp.Rational(23,5)),65)))
     err=abs(direct-gamma)/max(1,abs(gamma));maximum=max(maximum,err);assert err<mp.mpf('1e-60');checks+=1
 # Integer shifts must obey Gamma(z+1)=z Gamma(z) exactly.
 recurrence=0
 for a,b,c in [(1,1,1),(2,1,1),(1,2,2),(3,1,1)]:
  r=sp.sympify(str(coefficient(a,b,c,Q(17))));r2=sp.sympify(str(coefficient(a+1,b,c,Q(17))));A=a+b+c
  ratio=-(A-d/2)*(d-A-1)/(17*a*(d/2-a-b-1))
  assert sp.cancel(r2-r*ratio)==0;recurrence+=1
 product_checks=0
 for cc in triangle_cases('reserved'):
  rr=reduce(cc);assert rr and rr['success']
  rows=rr['blocks'][0]['result']['coefficients'];L=len(cc['definition']['loop_momenta']);scale=Q(cc['definition']['parameters']['Q']);dim=mp.mpf(23)/5;h=dim/2
  for t in cc['targets']:
   expected=mp.mpf(1)
   for i in range(L):
    a,b,c=t[3*i:3*i+3];A=a+b+c
    expected*=(-1)**A*mp.mpf(scale.numerator)**(2-A)*mp.gamma(A-h)*mp.gamma(h-a-b)*mp.gamma(h-b-c)*mp.gamma(dim-2)/(mp.gamma(2-h)*mp.gamma(h-1)**2*mp.gamma(dim-A)*mp.factorial(a-1)*mp.factorial(c-1))
   val=next(iter(rows[label(t)].values()));got=mp.mpf(str(sp.N(sp.sympify(val).subs(d,sp.Rational(23,5)),65)))
   assert abs(got-expected)/max(1,abs(expected))<mp.mpf('1e-57');product_checks+=1
 base=triangle(1,17,[[1,1,1]]);bad=[]
 for what in ['mass','second_scale','negative_power','extra_line','power_limit','cut']:
  cc=copy.deepcopy(base)
  if what=='mass':cc['definition']['propagators'][0]['mass_squared']='1'
  if what=='second_scale':cc['definition']['scalarproduct_rules'][0][1]='2'
  if what=='negative_power':cc['targets'][0][1]=-1
  if what=='extra_line':cc['definition']['propagators'].append(dict(momentum='k1-p2',mass_squared='0'));cc['targets'][0].append(1)
  if what=='power_limit':cc['targets'][0]=[4,4,4]
  if what=='cut':cc['definition']['cut_propagators']=[1]
  assert recognize(cc) is None;bad.append(what)
 write(HERE/'formula_checks.json',dict(complete=True,gamma_comparisons=checks,maximum_relative_error=str(maximum),exact_recurrence_checks=recurrence,product_gamma_checks=product_checks,product_loop_orders=list(range(1,14)),rejected_conditions=bad,source_sha256=sha(HERE/'s01_triangle.py'),comment='Numerical Gamma checks supplement the analytic derivation and exact native coefficient comparisons.'))
 print('formula checks',checks,recurrence,product_checks,flush=True)
if __name__=='__main__':main()
