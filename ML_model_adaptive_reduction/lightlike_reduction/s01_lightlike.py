"""Exact scalar and polynomial-numerator reductions at zero two-point invariant.

Feynman parameters and full d-dimensional angular moments avoid a Gram inverse.
The appendix derives the radial factor and the finite endpoint sum.
"""
from s00_light_common import Q,K,D,label,vector
from s16_rational import add as padd,mul as pmul
from functools import lru_cache
import math,time

class Unsupported(ValueError):pass

def poch(x,n):
 out=K.one
 if n>=0:
  for j in range(n):out*=x+j
 else:
  for j in range(1,1-n):out/=x-j
 return out

def eligible(c):
 d=c['definition'];ts=c['targets'];N=len(d['propagators'])
 return len(d['loop_momenta'])==1 and 1<=N<=5 and len(d['external_momenta'])<=4 and not d.get('cut_propagators') and not d.get('symbolic_ibp') and ts and all(len(t)==N and all(type(a)==int and abs(a)<=8 for a in t) and sum(max(-a,0) for a in t)<=4 and sum(max(a-1,0) for a in t)<=4 and sum(a>0 for a in t)<=2 for t in ts)

def reduce(c,deadline=None):
 if not eligible(c):return None
 start=time.perf_counter();d=c['definition'];N=len(d['propagators']);names=d['loop_momenta']+d['external_momenta'];E=len(names)-1
 try:
  vs=[vector(p['momentum'],names) for p in d['propagators']]
  if any(abs(v[0])!=1 for v in vs):return None
  shifts=[[-x*v[0] for x in v[1:]] for v in vs];masses=[Q(p['mass_squared']) for p in d['propagators']]
  rules={tuple(sorted(k)):Q(v) for k,v in d['scalarproduct_rules']}
  def dot(a,b):return sum((Q(a[i]*b[j])*rules[tuple(sorted([names[i+1],names[j+1]]))] for i in range(E) for j in range(E) if a[i]*b[j]),Q(0))
  cache={};terms_count=0
  def master(m):
   a=[0]*N;a[next(i for i,x in enumerate(masses) if x==m)]=1;return label(a)
  def one(a):
   nonlocal terms_count
   S=[i for i,v in enumerate(a) if v>0]
   if not S:return {}
   root=S[0];P=[x-y for x,y in zip(shifts[S[-1]],shifts[root])] if len(S)==2 else [0]*E
   if dot(P,P)!=0:raise Unsupported('nonzero two-point invariant')
   x=masses[root];y=masses[S[-1]]
   if not x and not y:return {}
   aa=a[root];bb=a[S[-1]] if len(S)==2 else 0;A=aa+bb
   neg=[i for i,v in enumerate(a) if v<0];R=[[x-y for x,y in zip(shifts[i],shifts[root])] for i in neg];pR=[dot(P,r) for r in R]
   constants=[(dot(r,r)-masses[i]-2*pR[j],2*pR[j]) for j,(i,r) in enumerate(zip(neg,R))]
   cov=[[ (dot(r,s)-pR[i]-pR[j],pR[i]+pR[j]) for j,s in enumerate(R)] for i,r in enumerate(R)]
   counts=(0,)*len(neg);full={(0,counts):(Q(1),)}
   for j,i in enumerate(neg):
    for _ in range(-a[i]):
     out={}
     def add(key,v):out[key]=padd(out.get(key,()),v)
     for (power,cs),poly in full.items():
      add((power,cs),pmul(poly,constants[j]));add((power+1,cs),poly)
      ns=list(cs);ns[j]+=1;add((power,tuple(ns)),tuple(2*v for v in poly))
     full={k:v for k,v in out.items() if v};terms_count+=len(full)
     if terms_count>100000 or deadline is not None and time.perf_counter()>deadline:raise Unsupported('exact work limit')
   @lru_cache(None)
   def wick(cs):
    if not sum(cs):return (Q(1),)
    if sum(cs)%2:return ()
    i=next(j for j,x in enumerate(cs) if x);a=list(cs);a[i]-=1;out=()
    for j,n in enumerate(a):
     if n:
      b=a.copy();b[j]-=1;v=pmul(cov[i][j],wick(tuple(b)));out=padd(out,tuple(n*x for x in v))
    return out
   moments={}
   for (power,cs),poly in full.items():
    if sum(cs)%2:continue
    h=sum(cs)//2;den=K.one
    for j in range(h):den*=D+2*j
    for t,v in enumerate(pmul(poly,wick(cs))):
     if v:moments[(power+h,t)]=moments.get((power+h,t),K.zero)+K(v)/den
   out={}
   def add(m,v):
    if m and v:
     k=master(m);out[k]=out.get(k,K.zero)+v
   for (h,t),v in moments.items():
    n=h-A+1;rad=((-1)**(A-h+1))*poch(D/2,h)*poch(1-D/2,A-h-1)
    if not bb:
     # No Feynman parameter for a single positive denominator.
     if t:raise Unsupported('unexpected parameter in tadpole')
     add(x,v*rad*(x**n)/math.factorial(A-1));continue
    rad/=math.factorial(aa-1)*math.factorial(bb-1)
    if x==y:
     beta=Q(math.factorial(aa+t-1)*math.factorial(bb-1),math.factorial(A+t-1))
     add(x,v*rad*beta*(x**n));continue
    delta=x-y
    for b in range(bb):
     k=aa-1+t+b;f=Q((-1)**b*math.comb(bb-1,b),1)/(delta**(k+1))
     for j in range(k+1):
      power=n+j+1;factor=f*math.comb(k,j)*((-y)**(k-j));r=v*rad*factor/(D/2+power-1)
      # A massless endpoint is scaleless by dimensional continuation.
      if x:add(x,r*(x**power))
      if y:add(y,-r*(y**power))
   return {k:str(v) for k,v in out.items() if v}
  rows={}
  for a in c['targets']:
   key=tuple(a)
   if key not in cache:cache[key]=one(a)
   rows[label(a)]=cache[key]
  return dict(success=True,status='completed',route='exact_lightlike_tensor',coefficients=rows,masters=[list(map(int,m.split(','))) for m in sorted({m for row in rows.values() for m in row})],model_used=False,attempts=[],expanded_terms=terms_count,analytic_seconds=time.perf_counter()-start)
 except (ValueError,KeyError,ZeroDivisionError,OverflowError):return None
