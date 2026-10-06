"""Exact Laurent polynomials in d and m2, and an independent partial-fraction oracle."""
from fractions import Fraction as F
from functools import lru_cache
from math import comb
P=lambda x: {} if not x else {(0,0):F(x)}
def clean(a):return {k:F(v) for k,v in a.items() if v}
def add(a,b):
 c=dict(a)
 for k,v in b.items():c[k]=c.get(k,0)+v
 return clean(c)
def scale(a,s):return clean({k:v*s for k,v in a.items()})
def mul(a,b):
 c={}
 for (i,j),v in a.items():
  for (k,l),w in b.items():c[i+k,j+l]=c.get((i+k,j+l),0)+v*w
 return clean(c)
def div(a,b):
 assert len(b)==1,b
 (i,j),v=next(iter(b.items()))
 return clean({(k-i,l-j):w/v for (k,l),w in a.items()})
def expr(a):
 if not a:return "0"
 out=[]
 for (i,j),v in sorted(a.items()):
  s=str(v.numerator) if v.denominator==1 else "("+str(v.numerator)+"/"+str(v.denominator)+")"
  if i:s+="*d**("+str(i)+")"
  if j:s+="*m2**("+str(j)+")"
  out.append(s)
 return "+".join(out).replace("+-","-")
def ev(a,point,p):
 return sum(v.numerator*pow(v.denominator,-1,p)*pow(point["d"],i,p)*pow(point["m2"],j,p) for (i,j),v in a.items())%p
def rowadd(a,b,f):
 c=dict(a)
 for k,v in b.items():
  z=add(c.get(k,{}),mul(f,v))
  if z:c[k]=z
  else:c.pop(k,None)
 return c
def terms(a):return [{"indices":list(k),"coefficient":expr(v)} for k,v in sorted(a.items())]
def key(a):return ",".join(map(str,a))
def field(a,point,p):return {key(k):z for k,v in a.items() if (z:=ev(v,point,p))}
def order(a):
 r=sum(max(0,x) for x in a);t=sum(x>0 for x in a)
 return (sum(1<<i for i,x in enumerate(a) if x>0),r-t,sum(max(0,-x) for x in a),r,a)
def compositions(n,r):
 if r==1:yield(n,);return
 for j in range(n+1):
  for tail in compositions(n-j,r-1):yield(j,)+tail
def all_b(r,maximum):
 return [b for n in range(1,maximum+1) for b in compositions(n,r)]
SAMPLES=[dict(sample=i,prime=p,point=dict(d=d,m2=m)) for i,(p,d,m) in enumerate(
 [(2147483647,37,7),(1000000007,41,11),(1000000009,43,17)])]
@lru_cache(maxsize=8192)
def oracle(L,rho,b):
 """Taylor coefficients of the rational integrand, independent of the row-reduction path."""
 B=sum(b);answer={}
 for j,bj in enumerate(b):
  if not bj:continue
  taylor=[F(1)]+[F(0)]*(bj-1)
  for i,bi in enumerate(b):
   if i==j or not bi:continue
   delta=rho[i]-rho[j]
   series=[F((-1)**t*comb(bi+t-1,t),delta**(bi+t)) for t in range(bj)]
   taylor=[sum(taylor[s]*series[t-s] for s in range(t+1)) for t in range(bj)]
  c={}
  for k in range(1,bj+1):
   product=P(1)
   for h in range(1,k):
    product=mul(product,{(0,0):F(L+h,h*rho[j]),(1,0):F(-L,2*h*rho[j])})
   c=add(c,scale(product,taylor[bj-k]))
  c={(i,m+1-B):v for (i,m),v in c.items()}
  if c:answer[(1,)*L+tuple(int(i==j) for i in range(len(b)))]=c
 return answer
def oracle_row(L,rho,row):
 out={}
 for a,c in row.items():out=rowadd(out,oracle(L,rho,a[L:]),c)
 return out
