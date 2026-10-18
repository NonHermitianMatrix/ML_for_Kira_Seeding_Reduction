"""Exact one-mass vacuum banana integrals with scalar or rank-one numerators."""
from s00_common import *

def structure(c):
 d=c['definition'];lm=d['loop_momenta'];L=len(lm);P=d['physical_propagators']
 if d.get('cut_propagators') or d.get('symbolic_ibp'):return None
 if d['external_momenta'] or L<2 or P!=L+1:return None
 massive=[j for j,p in enumerate(d['propagators'][:P]) if p['mass_squared']!='0']
 if len(massive)!=1:return None
 b=massive[0];q=d['propagators'][b]['momentum'].replace(' ','')
 if q not in ['+'.join(lm),'-'+'-'.join(lm)]:return None
 indices=[]
 for k in lm:
  hits=[j for j,p in enumerate(d['propagators'][:P]) if j!=b and p['momentum'].replace(' ','') in [k,'-'+k]]
  if len(hits)!=1:return None
  indices.append(hits[0])
 if len(set(indices))!=L:return None
 vectors={}
 for a in c['targets']:
  if any(v<1 for v in a[:P]):return None
  active=[j for j in range(P,len(a)) if a[j]!=0]
  if len(active)>1 or any(a[j]!=-1 for j in active):return None
  for j in active:
   p=d['propagators'][j]
   if p['mass_squared']!='0':return None
   text=p['momentum'].replace(' ','');tokens=re.findall(r'([+-]?)(?:(\d+)\*)?(k\d+)',text)
   rebuilt=''.join(sign+(number+'*' if number else '')+name for sign,number,name in tokens)
   if rebuilt!=text:return None
   v=[0]*L
   for sign,number,name in tokens:
    if name not in lm:return None
    v[lm.index(name)]+=(-1 if sign=='-' else 1)*int(number or 1)
   vectors[j]=v
 return dict(L=L,P=P,mass_index=b,massless_indices=indices,mass=d['propagators'][b]['mass_squared'],vectors=vectors)

def reduce(c,reference=False):
 info=structure(c)
 if info is None:return None
 import sympy as sp
 D=sp.Symbol('d');L=info['L'];P=info['P'];m=sp.sympify(info['mass'],rational=True)
 if m==0:return None
 def scalar(a,b):
  if b<1 or any(v<1 for v in a):return sp.Integer(0)
  A0=sum(a);A=A0+b;delta=A-P
  if reference:
   def coefficient(x,y):
    s=sum(x)
    return sp.gamma(s+y-L*D/2)*sp.gamma(s-(L-1)*D/2)*sp.prod(sp.gamma(D/2-v)/sp.gamma(v) for v in x)/sp.gamma(y)
   value=(-1)**delta*m**(-delta)*coefficient(a,b)/coefficient([1]*L,1)
   return sp.gammasimp(value)
  value=(-1)**delta*m**(-delta)*sp.rf(P-L*D/2,delta)*sp.rf(L-(L-1)*D/2,A0-L)/sp.factorial(b-1)
  for v in a:value/=sp.rf(D/2-v,v-1)*sp.factorial(v-1)
  return value
 rows={};basis=label([1]*P+[0]*(len(c['definition']['propagators'])-P))
 for target in c['targets']:
  a=[target[j] for j in info['massless_indices']];b=target[info['mass_index']]
  active=[j for j in range(P,len(target)) if target[j]!=0]
  if not active:value=scalar(a,b)
  else:
   v=info['vectors'][active[0]];alpha=[x-D/2 for x in a];lam=sum(alpha);value=sp.Integer(0)
   for i,ci in enumerate(v):
    if ci:
     shifted=list(a);shifted[i]-=1;value+=ci**2*scalar(shifted,b)
   if reference:
    cross=sum(2*v[i]*v[j]*alpha[i]*alpha[j] for i in range(L) for j in range(i+1,L))
    fourier_ratio=sp.gamma(lam+D/2-1)*sp.gamma(-lam)/(4*sp.gamma(lam+D/2)*sp.gamma(1-lam))
    moment=sp.gammasimp(-4*cross*fourier_ratio)
   else:moment=(sum(ci*x for ci,x in zip(v,alpha))**2-sum(ci**2*x**2 for ci,x in zip(v,alpha)))/(lam*(lam+D/2-1))
   value+=moment*(scalar(a,b-1)+m*scalar(a,b))
  value=sp.cancel(sp.gammasimp(value) if reference else value)
  rows[label(target)]={} if value==0 else {basis:str(value)}
 return dict(success=True,status='completed',route='one_mass_vacuum_gamma_check' if reference else 'one_mass_vacuum_scalar_or_rank_one',coefficients=rows,masters=[list(map(int,basis.split(',')))],model_used=False,attempts=[],analytic_assumptions=info)
