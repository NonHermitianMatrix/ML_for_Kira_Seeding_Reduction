"""Tensor and IBP identities with exact exceptional-sector leaves.

The appendix derives the transverse moments and the recurrence used here.
All kinematic values are rational; d remains symbolic. No predicted coefficient
or previously saved reduction enters the calculation.
"""
from fractions import Fraction as Q
from s01_lightlike import reduce as lightlike
from s11_coefficients import coefficient
from functools import lru_cache
import re,time
class Unsupported(ValueError):pass

def vector(text,names):
 text=str(text).replace(' ','');tokens=re.findall(r'([+-]?)(?:(\d+)\*)?([A-Za-z_]\w*)',text)
 if ''.join(s+(n+'*' if n else '')+v for s,n,v in tokens)!=text:raise Unsupported('momentum syntax')
 out=[0]*len(names)
 for sign,n,v in tokens:
  if v not in names:raise Unsupported('unknown momentum')
  out[names.index(v)]+=(-1 if sign=='-' else 1)*int(n or 1)
 return out

def inverse(M):
 n=len(M);a=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(M)]
 for j in range(n):
  k=next((i for i in range(j,n) if a[i][j]),None)
  if k is None:raise Unsupported('singular kinematic matrix')
  a[j],a[k]=a[k],a[j];v=a[j][j];a[j]=[x/v for x in a[j]]
  for i in range(n):
   if i!=j and a[i][j]:
    v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[j])]
 return [r[n:] for r in a]

def eligible(c):
 d=c['definition'];n=len(d['propagators']);ts=c['targets']
 return len(d['loop_momenta'])==1 and 2<=n<=5 and len(d['external_momenta'])==n-1 and not d.get('cut_propagators') and not d.get('symbolic_ibp') and ts and any(any(v<0 for v in a) for a in ts) and all(len(a)==n and all(type(v)==int and abs(v)<=8 for v in a) and sum(max(-v,0) for v in a)<=6 and sum(max(v-1,0) for v in a)<=6 for a in ts)

def reduce(c,action='tensor_largest',deadline=None):
 if not eligible(c):return None
 start=time.perf_counter();d=c['definition'];ts=c['targets'];n=len(d['propagators']);names=d['loop_momenta']+d['external_momenta'];E=n-1
 try:
  vs=[vector(p['momentum'],names) for p in d['propagators']]
  if any(abs(v[0])!=1 for v in vs):return None
  shifts=[[-x*v[0] for x in v[1:]] for v in vs]
  masses=[Q(p['mass_squared']) for p in d['propagators']]
  rules={tuple(sorted(pair)):Q(v) for pair,v in d['scalarproduct_rules']}
  def dot(a,b):return sum((Q(a[i]*b[j])*rules[tuple(sorted([names[i+1],names[j+1]]))] for i in range(E) for j in range(E) if a[i]*b[j]),Q(0))
  Y=[[masses[i]+masses[j]-dot([x-y for x,y in zip(shifts[i],shifts[j])],[x-y for x,y in zip(shifts[i],shifts[j])]) for j in range(n)] for i in range(n)]
  from s16_rational import K,D
  QQ=Q;zero=K.zero;one=K.one
  def scalar(q):return K(QQ(q.numerator,q.denominator)) if isinstance(q,Q) else K(q)
  z=(0,)*n;nodes=0;angular_calls=0;polynomial_terms=0
  def check():
   if nodes>12000 or polynomial_terms>200000 or (deadline is not None and time.perf_counter()>deadline):raise Unsupported('exact work limit')
  def plus(out,p,f=Q(1)):
   for m,v in p.items():
    a=out.get(m,Q(0))+f*v
    if a:out[m]=a
    else:out.pop(m,None)
   return out
  def mul(p,q):
   out={}
   for a,x in p.items():
    for b,y in q.items():
     m=tuple(i+j for i,j in zip(a,b));out[m]=out.get(m,Q(0))+x*y
   return {m:v for m,v in out.items() if v}
  def mon(i):a=list(z);a[i]=1;return {tuple(a):Q(1)}
  def linear(constant,terms):
   out={z:constant} if constant else {}
   for j,value in terms.items():plus(out,mon(j),value)
   return out
  def rowadd(out,row,value):
   if not value:return
   for m,v in row.items():
    a=out.get(m,zero)+value*v
    if a:out[m]=a
    else:out.pop(m,None)
  @lru_cache(None)
  def cayley(S):return inverse([[Y[i][j] for j in S] for i in S])
  @lru_cache(None)
  def angular(S,neg):
   nonlocal angular_calls,polynomial_terms
   angular_calls+=1;check();root=S[0];others=S[1:];R=[[x-y for x,y in zip(shifts[j],shifts[root])] for j in range(n)]
   G=inverse([[dot(R[i],R[j]) for j in others] for i in others]) if others else []
   u=[linear((masses[root]-masses[i]+dot(R[i],R[i]))/2,{root:Q(1,2),i:Q(-1,2)}) for i in others]
   perpendicular=linear(masses[root],{root:Q(1)})
   for i in range(len(others)):
    for j in range(len(others)):plus(perpendicular,mul(u[i],u[j]),-G[i][j])
   negidx=[i for i,v in enumerate(neg) if v];r=len(negidx);zz=(0,)*r
   B=[];proj=[]
   for j in negidx:
    weights=[sum((dot(R[j],R[i])*G[k][h] for k,i in enumerate(others)),Q(0)) for h in range(len(others))]
    b=linear(masses[root]+dot(R[j],R[j])-masses[j],{root:Q(1)})
    for w,ui in zip(weights,u):plus(b,ui,-2*w)
    B.append(b);proj.append(weights)
   covariance=[[dot(R[i],R[j])-sum((w*dot(R[h],R[j]) for w,h in zip(proj[a],others)),Q(0)) for j in negidx] for a,i in enumerate(negidx)]
   full={(z,zz):Q(1)}
   for j,i in enumerate(negidx):
    for _ in range(neg[i]):
     out={}
     for (dm,zm),v in full.items():
      for bm,bv in B[j].items():
       key=(tuple(a+b for a,b in zip(dm,bm)),zm);out[key]=out.get(key,Q(0))+v*bv
      zm1=list(zm);zm1[j]+=1;key=(dm,tuple(zm1));out[key]=out.get(key,Q(0))-2*v
     full={m:v for m,v in out.items() if v};polynomial_terms+=len(full);check()
   @lru_cache(None)
   def wick(counts):
    total=sum(counts)
    if not total:return Q(1)
    if total%2:return Q(0)
    i=next(j for j,x in enumerate(counts) if x);a=list(counts);a[i]-=1;out=Q(0)
    for j,x in enumerate(a):
     if x and covariance[i][j]:
      b=a.copy();b[j]-=1;out+=x*covariance[i][j]*wick(tuple(b))
    return out
   grouped={}
   for (dm,zm),v in full.items():
    w=wick(zm)
    if w:
     k=sum(zm)//2;p=grouped.setdefault(k,{});p[dm]=p.get(dm,Q(0))+v*w
   powers=[{z:Q(1)}]
   for k in range(max(grouped,default=0)):powers.append(mul(powers[-1],perpendicular))
   out={};den=one
   for k in range(len(powers)):
    if k:den*=D-(len(S)-1)+2*(k-1)
    for dm,v in mul(grouped.get(k,{}),powers[k]).items():
     out[dm]=out.get(dm,zero)+scalar(v)/den
   return {m:v for m,v in out.items() if v}
  @lru_cache(None)
  def rec(a):
   nonlocal nodes
   nodes+=1;check();S=tuple(i for i,v in enumerate(a) if v>0);neg=tuple(max(-v,0) for v in a);dots=[i for i in S if a[i]>1]
   if not S or all(not Y[i][j] for i in S for j in S):return {}
   if len(S)==2:
    delta=[x-y for x,y in zip(shifts[S[-1]],shifts[S[0]])]
    if dot(delta,delta)==0:
     cc=dict(c,targets=[list(a)],size=1);exact=lightlike(cc,deadline=deadline)
     if exact is not None:return {tuple(map(int,m.split(','))):coefficient(v) for m,v in exact['coefficients'][','.join(map(str,a))].items()}
   if any(neg) and (action.startswith('tensor') or not dots):
    out={}
    for powers,v in angular(S,neg).items():
     b=tuple(a[i]-powers[i] if i in S else 0 for i in range(n));rowadd(out,rec(b),v)
    return out
   if not dots:return {a:one}
   j=(max if action.endswith('largest') else min)(dots,key=lambda i:a[i]);b=list(a);b[j]-=1;b=tuple(b);B=sum(b);weights=[v/b[j] for v in cayley(S)[S.index(j)]];out={};base=rec(b)
   rowadd(out,base,scalar(sum(weights,Q(0)))*(D-B)-scalar(sum((w*b[i] for w,i in zip(weights,S)),Q(0))))
   for w,i in zip(weights,S):
    if not w:continue
    for ell in range(n):
     if ell==i or b[ell]==0:continue
     shifted=list(b);shifted[ell]+=1;shifted[i]-=1;rowadd(out,rec(tuple(shifted)),scalar(-w*b[ell]))
    for ell in range(n):
     if b[ell]<0 and Y[i][ell]:
      shifted=list(b);shifted[ell]+=1;rowadd(out,rec(tuple(shifted)),scalar(-w*b[ell]*Y[i][ell]))
   return out
  label=lambda a:','.join(map(str,a));rows={label(a):{label(m):str(v) for m,v in rec(tuple(a)).items()} for a in ts};masters=sorted({tuple(map(int,m.split(','))) for row in rows.values() for m in row})
  return dict(success=True,status='completed',route='exact_one_loop_tensor',coefficients=rows,masters=[list(a) for a in masters],model_used=False,attempts=[],recurrence_states=nodes,angular_patterns=angular_calls,polynomial_terms=polynomial_terms,action=action,analytic_seconds=time.perf_counter()-start)
 except (Unsupported,ValueError,KeyError,ZeroDivisionError):return None
