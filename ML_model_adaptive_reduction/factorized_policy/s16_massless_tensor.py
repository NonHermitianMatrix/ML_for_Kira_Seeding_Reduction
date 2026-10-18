"""Exact massless two-point convolution with at most one quadratic numerator."""
from s00_common import *

def vector(text,names):
 text=text.replace(' ','');tokens=re.findall(r'([+-]?)(?:(\d+)\*)?([kp]\d+)',text)
 if ''.join(sign+(n+'*' if n else '')+v for sign,n,v in tokens)!=text:return None
 out=[0]*len(names)
 for sign,n,v in tokens:
  if v not in names:return None
  out[names.index(v)]+=(-1 if sign=='-' else 1)*int(n or 1)
 return out

def reduce(c,reference=False):
 d=c['definition'];L=len(d['loop_momenta']);P=d['physical_propagators'];N=len(d['propagators'])
 if d.get('cut_propagators') or d.get('symbolic_ibp') or len(d['external_momenta'])!=1 or P!=L+1:return None
 if any(p['mass_squared']!='0' for p in d['propagators']):return None
 if not any(any(a[P:]) for a in c['targets']):return None
 names=d['loop_momenta']+d['external_momenta'];vs=[vector(p['momentum'],names) for p in d['propagators']]
 if any(v is None for v in vs):return None
 indices=[]
 for i in range(L):
  unit=[int(j==i) for j in range(L+1)];hits=[j for j,v in enumerate(vs[:P]) if v in [unit,[-x for x in unit]]]
  if len(hits)!=1:return None
  indices.append(hits[0])
 tail=[j for j in range(P) if j not in indices]
 if len(tail)!=1:return None
 total=[-1]*L+[1]
 if vs[tail[0]] not in [total,[-x for x in total]]:return None
 indices.append(tail[0])
 for a in c['targets']:
  if any(x<1 for x in a[:P]):return None
  active=[j for j in range(P,N) if a[j]]
  if len(active)>1 or any(a[j]!=-1 for j in active):return None
 external=d['external_momenta'][0];rules=[value for pair,value in d['scalarproduct_rules'] if pair==[external,external]]
 if len(rules)!=1:return None
 import sympy as sp
 D=sp.Symbol('d');p2=sp.sympify(rules[0],rational=True)
 if p2==0:return None
 def scalar(a):
  if any(v<1 for v in a):return sp.Integer(0)
  A=sum(a);delta=A-P
  if reference:
   def C(x):return sp.gamma(sum(x)-L*D/2)/sp.gamma(P*D/2-sum(x))*sp.prod(sp.gamma(D/2-v)/sp.gamma(v) for v in x)
   return sp.gammasimp(p2**(-delta)*C(a)/C([1]*P))
  value=sp.rf(P-L*D/2,delta)*sp.rf(P*D/2-P-delta,delta)/p2**delta
  for v in a:value/=sp.rf(D/2-v,v-1)*sp.factorial(v-1)
  return value
 rows={};basis=label([1]*P+[0]*(N-P))
 for target in c['targets']:
  a=[target[j] for j in indices];active=[j for j in range(P,N) if target[j]]
  if not active:value=scalar(a)
  else:
   v=vs[active[0]];w=[x+v[-1] for x in v[:-1]]+[v[-1]];beta=[x-D/2 for x in a];lam=sum(beta);value=sp.Integer(0)
   for i,wi in enumerate(w):
    if wi:
     shifted=list(a);shifted[i]-=1;value+=wi**2*scalar(shifted)
   cross=sum(2*w[i]*w[j]*beta[i]*beta[j] for i in range(P) for j in range(i+1,P)) if reference else sum(x*y for x,y in zip(w,beta))**2-sum(x*x*y*y for x,y in zip(w,beta))
   factor=sp.gammasimp(-cross*sp.gamma(lam+D/2-1)*sp.gamma(-lam)/(sp.gamma(lam+D/2)*sp.gamma(1-lam))) if reference else cross/(lam*(lam+D/2-1))
   value+=factor*p2*scalar(a)
  value=sp.cancel(sp.gammasimp(value) if reference else value);rows[label(target)]={} if value==0 else {basis:str(value)}
 return dict(success=True,status='completed',route='massless_quadratic_gamma_check' if reference else 'massless_quadratic_convolution',coefficients=rows,masters=[list(map(int,basis.split(',')))],model_used=False,attempts=[])
