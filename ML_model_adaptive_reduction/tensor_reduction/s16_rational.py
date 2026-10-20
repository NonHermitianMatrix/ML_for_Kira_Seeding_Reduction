"""Exact rational functions of d with factored integer-shift denominators.

Angular moments introduce only factors (d+j). Scalar IBP adds polynomials.
Store these factors explicitly and cancel them by exact synthetic division.
"""
from fractions import Fraction as Q

def trim(a):
 a=list(a)
 while a and not a[-1]:a.pop()
 return tuple(a)
def add(a,b):return trim([ (a[i] if i<len(a) else Q(0))+(b[i] if i<len(b) else Q(0)) for i in range(max(len(a),len(b)))])
def mul(a,b):
 if not a or not b:return ()
 out=[Q(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):out[i+j]+=x*y
 return trim(out)
def divide_linear(a,offset):
 if len(a)<2:return None
 b=[Q(0)]*(len(a)-1);b[-1]=a[-1]
 for j in range(len(b)-2,-1,-1):b[j]=a[j+1]-offset*b[j+1]
 return trim(b) if a[0]==offset*b[0] else None

def make(n,den):
 n=trim(n);den=dict(den)
 if not n:den={}
 else:
  for j in list(den):
   while den[j]:
    q=divide_linear(n,j)
    if q is None:break
    n=q;den[j]-=1
   if not den[j]:del den[j]
 r=object.__new__(R);r.n=n;r.den=tuple(sorted(den.items()));return r
class R:
 __slots__=('n','den')
 def __init__(self,q=0):self.n=(Q(q),) if q else ();self.den=()
 def __bool__(self):return bool(self.n)
 def __neg__(self):return make([-v for v in self.n],self.den)
 def __add__(self,b):
  if not isinstance(b,R):b=R(b)
  if not self:return b
  if not b:return self
  da=dict(self.den);db=dict(b.den);both={j:max(da.get(j,0),db.get(j,0)) for j in set(da)|set(db)}
  a=self.n;c=b.n
  for j,m in both.items():
   for _ in range(m-da.get(j,0)):a=mul(a,(Q(j),Q(1)))
   for _ in range(m-db.get(j,0)):c=mul(c,(Q(j),Q(1)))
  return make(add(a,c),both)
 __radd__=__add__
 def __sub__(self,b):return self+(-b if isinstance(b,R) else -Q(b))
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  if not isinstance(b,R):b=R(b)
  if not self or not b:return R(0)
  den=dict(self.den)
  for j,m in b.den:den[j]=den.get(j,0)+m
  return make(mul(self.n,b.n),den)
 __rmul__=__mul__
 def __truediv__(self,b):
  if not isinstance(b,R):b=R(b)
  if not b:raise ZeroDivisionError
  if not self:return R(0)
  n=b.n;den=dict(self.den)
  for j in range(-16,17):
   while len(n)>1:
    q=divide_linear(n,j)
    if q is None:break
    n=q;den[j]=den.get(j,0)+1
  if len(n)!=1:raise ValueError('Denominator is outside the derived angular-factor domain')
  a=tuple(v/n[0] for v in self.n)
  for j,m in b.den:
   for _ in range(m):a=mul(a,(Q(j),Q(1)))
  return make(a,den)
 def __rtruediv__(self,b):return R(b)/self
 def __str__(self):
  if not self:return '0'
  terms=[]
  for i,q in enumerate(self.n):
   if not q:continue
   coeff=str(q.numerator) if q.denominator==1 else '('+str(q.numerator)+'/'+str(q.denominator)+')'
   terms.append(coeff if i==0 else coeff+'*d'+('**'+str(i) if i>1 else ''))
  numerator='('+'+'.join(terms)+')' if len(terms)>1 else terms[0]
  if not self.den:return numerator
  factors=[]
  for j,m in self.den:
   f='d' if j==0 else '(d'+('+' if j>0 else '')+str(j)+')'
   factors.append(f if m==1 else f+'**'+str(m))
  return numerator+'/('+'*'.join(factors)+')'
class Ring:
 zero=R(0);one=R(1)
 def __call__(self,q):return q if isinstance(q,R) else R(q)
K=Ring();D=make([Q(0),Q(1)],{})
