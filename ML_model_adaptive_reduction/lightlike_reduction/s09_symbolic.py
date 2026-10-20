"""Symbolic scalar tadpoles and zero-invariant bubbles by mass derivatives."""
from s00_light_common import label,vector
import math,time

def reduce(c):
 definition=c['definition'];N=len(definition['propagators'])
 if len(definition['loop_momenta'])!=1 or definition.get('cut_propagators') or definition.get('symbolic_ibp') or not definition.get('invariants'):return None
 if any(len(t)!=N or any(type(a)!=int or not 0<=a<=6 for a in t) or sum(a>0 for a in t)>2 or sum(t)>8 for t in c['targets']):return None
 import sympy as s
 start=time.perf_counter();d=s.Symbol('d');q=d/2-1
 try:
  allowed={str(k):s.Symbol(str(k)) for k,*_ in definition['invariants']};names=definition['loop_momenta']+definition['external_momenta'];E=len(names)-1
  def parse(v):
   r=s.sympify(v,locals=allowed)
   if not r.is_rational_function(*allowed.values()) or not r.free_symbols<=set(allowed.values()):raise ValueError('unsupported symbolic input')
   return r
  masses=[parse(p['mass_squared']) for p in definition['propagators']];vs=[vector(p['momentum'],names) for p in definition['propagators']]
  if any(abs(v[0])!=1 for v in vs):return None
  shifts=[[-x*v[0] for x in v[1:]] for v in vs];rules={tuple(sorted(k)):parse(v) for k,v in definition['scalarproduct_rules']}
  def master(m):
   t=[0]*N;t[next(i for i,x in enumerate(masses) if s.cancel(x-m)==0)]=1;return label(t)
  rows={}
  X,Y=s.symbols('_x _y');cache={}
  for a in c['targets']:
   S=[i for i,x in enumerate(a) if x>0];row={}
   if not S:rows[label(a)]={};continue
   i=S[0];x=masses[i];aa=a[i]
   if len(S)==1:
    if x:row[master(x)]=s.prod(q-j for j in range(aa-1))/(math.factorial(aa-1)*x**(aa-1))
   else:
    j=S[1];y=masses[j];bb=a[j];P=[u-v for u,v in zip(shifts[i],shifts[j])]
    if s.cancel(sum(P[u]*P[v]*rules[tuple(sorted([names[u+1],names[v+1]]))] for u in range(E) for v in range(E)))!=0:return None
    if s.cancel(x-y)==0:
     if x:row[master(x)]=s.prod(q-k for k in range(aa+bb-1))/(math.factorial(aa+bb-1)*x**(aa+bb-1))
    else:
     # Keep independent formal masses until all derivatives are complete.
     key=(aa,bb)
     if key not in cache:
      cx=1/(X-Y);cy=-cx
      for _ in range(aa-1):cx=s.cancel(s.diff(cx,X)+q*cx/X);cy=s.diff(cy,X)
      for _ in range(bb-1):cx=s.diff(cx,Y);cy=s.cancel(s.diff(cy,Y)+q*cy/Y)
      f=math.factorial(aa-1)*math.factorial(bb-1);cache[key]=(s.cancel(cx/f),s.cancel(cy/f))
     for m,z in zip([x,y],cache[key]):
      if m:row[master(m)]=row.get(master(m),0)+z.subs({X:x,Y:y},simultaneous=True)
   rows[label(a)]={m:str(s.cancel(v)) for m,v in row.items() if s.cancel(v)!=0}
  return dict(success=True,status='completed',route='exact_symbolic_lightlike_scalar',coefficients=rows,masters=[list(map(int,m.split(','))) for m in sorted({m for row in rows.values() for m in row})],model_used=False,attempts=[],analytic_seconds=time.perf_counter()-start)
 except (ValueError,TypeError,KeyError,ZeroDivisionError):return None
