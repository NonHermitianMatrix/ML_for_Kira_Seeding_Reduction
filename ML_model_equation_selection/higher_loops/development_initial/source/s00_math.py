"""Exact restricted vacuum identities and coefficient-free dependency choices."""
import itertools, json, math
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FEATURES=["massive_slots","total_power","active_slots","pair_min","pair_max","pair_sum","pair_product","other_max","other_sum","other_active","smallest_power","largest_power"]
def compositions(n,r):
 if r==1:
  yield (n,);return
 for a in range(n+1):
  for b in compositions(n-a,r-1):yield (a,)+b
def children(b,pair):
 out=[]
 for j in pair:
  a=list(b);a[j]-=1;out.append(tuple(a))
 return tuple(out)
def pairs(b):return list(itertools.combinations([j for j,v in enumerate(b) if v],2))
def features(b,p):
 vals=[v for v in b if v];i,j=p;o=[v for k,v in enumerate(b) if k not in p and v]
 return [len(b),sum(b),len(vals),min(b[i],b[j]),max(b[i],b[j]),b[i]+b[j],b[i]*b[j],max(o,default=0),sum(o),len(o),min(vals),max(vals)]
@lru_cache(maxsize=8192)
def teacher(b):
 if sum(b)==1:return frozenset(),()
 pp=pairs(b)
 if not pp:
  j=next(i for i,v in enumerate(b) if v);a=list(b);a[j]-=1
  return teacher(tuple(a))[0]|{b},(j,)
 alternatives=[]
 for p in pp:
  x,y=children(b,p);union=teacher(x)[0]|teacher(y)[0]|{b}
  alternatives.append((len(union),p,union))
 _,p,u=min(alternatives,key=lambda x:(x[0],x[1]))
 return u,p
def score(nodes,x):
 i=0
 while nodes[i]["feature"]>=0:
  n=nodes[i];i=n["left"] if x[n["feature"]]<=n["threshold"] else n["right"]
 return nodes[i]["probability"]
def choose(b,mode,nodes=None):
 pp=pairs(b)
 if not pp:return (next(i for i,v in enumerate(b) if v),)
 if mode=="learned":
  return max(pp,key=lambda p:(score(nodes,features(b,p)),-p[0],-p[1]))
 if mode=="smallest":return min(pp,key=lambda p:(b[p[0]]+b[p[1]],max(b[p[0]],b[p[1]]),p))
 if mode=="largest":return min(pp,key=lambda p:(-b[p[0]]-b[p[1]],-max(b[p[0]],b[p[1]]),p))
 if mode=="extreme":
  a=[i for i,v in enumerate(b) if v];return tuple(sorted((min(a,key=lambda i:(b[i],i)),max(a,key=lambda i:(b[i],i)))))
 if mode=="teacher":return teacher(b)[1]
 assert mode=="first";return pp[0]
def closure(targets,mode,nodes=None):
 rows={};pending=list(map(tuple,targets));decisions=0
 while pending:
  b=pending.pop()
  if sum(b)==1 or b in rows:continue
  p=choose(b,mode,nodes);rows[b]=p
  if len(p)==1:
   a=list(b);a[p[0]]-=1;pending.append(tuple(a))
  else:
   pending.extend(children(b,p));decisions+=1
 return rows,decisions
def dense(r,maximum):
 out=[]
 for B in range(2,maximum+2):
  for b in compositions(B,r):
   for p in pairs(b):out.append((b,p))
 for B in range(1,maximum+1):
  for b in compositions(B,r):out.append((b,None))
 return out
def validate(request):
 assert request["family"]=="coupled_vacuum_unit_massless"
 rho=request["mass_ratios"];r=len(rho)
 assert 2<=r<=4 and all(isinstance(x,int) and x>0 for x in rho) and len(set(rho))==r
 loops=request["loops"]
 assert loops and len(set(loops))==len(loops) and all(isinstance(x,int) and x>0 for x in loops)
 assert len(loops)<=32
 targets=request["targets"]
 assert 0<len(targets)<=128 and len(set(map(tuple,targets)))==len(targets)
 assert all(len(b)==r and all(isinstance(v,int) and v>=0 for v in b) and 1<=sum(b)<=14 for b in targets)
 assert request.get("mass_scale_squared",1)==1
 return r
def equation(b,p,rho,L=None):
 # L=None uses z=L*(d-2), retaining exact symbolic dimensional dependence.
 r=len(b);B=sum(b)
 if p is None:
  row={b:(str(L)+"*d-"+str(2*(L+B))) if L else "z-"+str(2*B)}
  for j,bj in enumerate(b):
   if bj:
    a=list(b);a[j]+=1;row[tuple(a)]=str(2*bj*rho[j])
  return row
 if len(p)==1:
  j=p[0];a=list(b);a[j]-=1;k=a[j]
  return {b:str(2*k*rho[j]),tuple(a):(str(L)+"*d-"+str(2*(L+k))) if L else "z-"+str(2*k)}
 i,j=p;a,c=children(b,p)
 return {b:str(rho[i]-rho[j]),a:"-1",c:"1"}
def poly_substitute(p,L):
 out={}
 for n,c in enumerate(p):
  for k in range(n+1):out[k]=out.get(k,F(0))+c*math.comb(n,k)*L**k*(-2*L)**(n-k)
 return [out.get(k,F(0)) for k in range(max(out,default=0)+1)]
def rational_polynomial(s,symbol):
 # Kira emits rational functions; this domain must reduce to a polynomial.
 import sympy as sp
 x=sp.Symbol(symbol);expr=sp.cancel(sp.sympify(s.replace("^","**"),rational=True))
 p=sp.Poly(expr,x,domain=sp.QQ)
 if p.is_zero:return []
 return [F(str(p.nth(k))) for k in range(p.degree()+1)]
def canonical(p):
 p=list(p)
 while p and p[-1]==0:p.pop()
 return tuple(p)
def oracle(L,rho,b):
 # Independent Taylor partial fractions, not the selected dependency path.
 from math import comb
 out={}
 for j,bj in enumerate(b):
  if not bj:continue
  series=[F(1)]+[F(0)]*(bj-1)
  for i,bi in enumerate(b):
   if i==j or not bi:continue
   delta=rho[i]-rho[j]
   t=[F((-1)**k*comb(bi+k-1,k),delta**(bi+k)) for k in range(bj)]
   series=[sum(series[h]*t[k-h] for h in range(k+1)) for k in range(bj)]
  result=[]
  for k in range(1,bj+1):
   product=[F(1)]
   for h in range(1,k):
    a=F(L+h,h*rho[j]);c=F(-L,2*h*rho[j]);n=[F(0)]*(len(product)+1)
    for v,x in enumerate(product):n[v]+=a*x;n[v+1]+=c*x
    product=n
   while len(result)<len(product):result.append(F(0))
   for v,x in enumerate(product):result[v]+=series[bj-k]*x
  out[j]=canonical(result)
 return out
def write(path,x):
 path.parent.mkdir(parents=True,exist_ok=True);t=path.with_suffix(path.suffix+".tmp");t.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");t.replace(path)
