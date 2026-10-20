"""Exact one-scale massless triangles and products of independent triangles."""
from s00_triangle_common import ROOT,label
from fractions import Fraction as Q
import math,sys,time
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/tensor_reduction'))
from s17_fast_tensor import vector
from s16_rational import K,D

def recognize(c):
 d=c['definition'];lm=d['loop_momenta'];em=d['external_momenta'];ps=d['propagators'];ts=c['targets'];L=len(lm)
 if not 1<=L<=13 or not em or not ts or d.get('cut_propagators') or d.get('symbolic_ibp'):return None
 if len(ps)>128 or any(len(t)!=len(ps) or any(type(a)!=int or not 0<=a<=4 for a in t) for t in ts):return None
 try:
  rules={tuple(sorted(pair)):Q(v) for pair,v in d['scalarproduct_rules']}
  vs=[vector(p['momentum'],lm+em) for p in ps];groups=[];used=set()
  def norm(v):return sum((Q(a*b)*rules[tuple(sorted((em[i],em[j])))] for i,a in enumerate(v) for j,b in enumerate(v) if a*b),Q(0))
  for k in range(L):
   ids=[j for j,v in enumerate(vs) if abs(v[k])==1 and sum(bool(x) for x in v[:L])==1]
   if len(ids)!=3 or any(Q(ps[j]['mass_squared']) for j in ids):return None
   shifts={j:[Q(x,vs[j][k]) for x in vs[j][L:]] for j in ids}
   edges=[(i,j,-norm([x-y for x,y in zip(shifts[i],shifts[j])])) for ii,i in enumerate(ids) for j in ids[ii+1:]]
   nonzero=[e for e in edges if e[2]]
   if len(nonzero)!=1 or nonzero[0][2]<=0:return None
   a,z,scale=nonzero[0];b=next(j for j in ids if j not in [a,z])
   if any(sum(t[j] for j in ids)>8 for t in ts):return None
   groups.append((a,b,z,scale));used.update(ids)
  if any(t[j] for t in ts for j in range(len(ps)) if j not in used):return None
  return groups
 except (ValueError,KeyError,ZeroDivisionError,TypeError):return None

def poch(z,n):
 r=K.one
 if n>=0:
  for j in range(n):r*=z+j
 else:
  for j in range(1,1-n):r/=z-j
 return r

def coefficient(a,b,c,scale):
 if not a or not c:return K.zero
 A=a+b+c;h=D/2
 return K(Q((-1)**A)*scale**(2-A)/math.factorial(a-1)/math.factorial(c-1))*poch(2-h,A-2)*poch(h-1,1-a-b)*poch(h-1,1-b-c)*poch(D-A,A-2)

def reduce(c):
 start=time.perf_counter();groups=recognize(c)
 if groups is None:return None
 n=len(c['definition']['propagators']);master=[0]*n
 for a,b,z,q in groups:master[a]=master[z]=1
 key=label(master);rows={};memo={}
 for t in c['targets']:
  factors=[];zero=False
  for a,b,z,q in groups:
   k=(t[a],t[b],t[z],q)
   if k not in memo:memo[k]=coefficient(*k)
   if not memo[k]:zero=True;break
   factors.append(str(memo[k]))
  if zero:rows[label(t)]={}
  else:
   # Keep the physical factorization: avoid expanding cross-loop polynomials.
   from collections import Counter
   counts=Counter(v for v in factors if v!='1')
   value='*'.join('('+v+')'+('**'+str(n) if n>1 else '') for v,n in counts.items()) or '1'
   rows[label(t)]={key:value}
 masters=[master] if any(rows.values()) else []
 values={key:dict(formula='product(Q^(d/2-2)*Gamma(2-d/2)*Gamma(d/2-1)^2/Gamma(d-2))',scales=[str(g[3]) for g in groups])} if masters else {}
 result=dict(success=True,status='completed',route='exact_one_scale_triangle',coefficients=rows,masters=masters,master_values=values,analytic_evaluation_complete=True,model_used=False,attempts=[],coefficient_evaluations=len(memo),component_products_preserved=True,normalization='d^d k/(i*pi^(d/2)); denominators q^2+i0; Q=-s>0; dimensional continuation')
 return dict(success=True,status='completed',blocks=[dict(case=c,indices=list(range(n)),result=result)],model_used=False,total_seconds=time.perf_counter()-start)
