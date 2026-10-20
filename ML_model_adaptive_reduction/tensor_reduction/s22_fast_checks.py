"""Check the factored rational arithmetic against independent symbolic arithmetic."""
from s00_tensor_common import *
from s16_rational import K,D
from s17_fast_tensor import reduce
from s03_cases import case
import sympy as sp

def main():
 rng=random.Random(7717);d=sp.Symbol('d');checks=0
 for i in range(80):
  a=K(rng.randint(-9,9))+D*rng.randint(-5,5)+D*D*rng.randint(-4,4)
  b=D+rng.randint(-5,5);c=D+rng.randint(-5,5);x=a/(b*c);y=(D+rng.randint(-8,8))/(c*c)
  for ans,ref in [(x+y,sp.sympify(str(x))+sp.sympify(str(y))),(x*y,sp.sympify(str(x))*sp.sympify(str(y))),((x*b)*c,sp.sympify(str(a)))]:
   assert sp.cancel(sp.sympify(str(ans))-ref)==0;checks+=1
 h=previous().batch.legacy().h;native_checks=0
 for f in sorted((HERE/'development').glob('*.json.gz')):
  row=read(f);r=reduce(row['case']);assert r is not None
  ok,n=h.equal(r['coefficients'],row['native']['coefficients']);assert ok,f.name;native_checks+=n
 # Protect the physics recurrence from an accidental change during the field refactor.
 old=(HERE/'s01_tensor.py').read_text();new=(HERE/'s17_fast_tensor.py').read_text()
 expected=old.replace('from sympy.polys.fields import field\n  from sympy import QQ\n  K,D=field(\'d\',QQ);zero=K.zero;one=K.one','from s16_rational import K,D\n  QQ=Q;zero=K.zero;one=K.one').replace('"""Exact angular tensor reduction and signed-index one-loop IBP recurrence.','"""The same tensor and IBP identities with factored dimension denominators.')
 assert new==expected
 write(HERE/'fast_arithmetic_checks.json',dict(complete=True,algebra_checks=checks,native_coefficients=native_checks,physics_recurrence_unchanged=True))
 print(json.dumps(dict(fast_checks=True,algebra_checks=checks,native_coefficients=native_checks)),flush=True)
if __name__=='__main__':main()
