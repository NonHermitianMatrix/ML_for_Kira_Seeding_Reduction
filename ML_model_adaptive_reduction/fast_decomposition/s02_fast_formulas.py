"""Exact finite products for tadpoles, massless propagators, and one-mass vacua."""
from s00_fast_common import label
from s01_fast_recurrence import vector
import math

def par(x):return '('+str(x)+')'
def prod(xs):return '*'.join(par(x) for x in xs) or '1'
def rf(x,n):return prod([par(x)+'+'+str(i) for i in range(n)])
def result(c,rows,route):
 P=c['definition']['physical_propagators'];N=len(c['definition']['propagators']);m=[1]*P+[0]*(N-P)
 return dict(success=True,status='completed',route=route,coefficients=rows,masters=[m] if any(rows.values()) else [],model_used=False,attempts=[])

def reduce(c):
 d=c['definition'];L=len(d['loop_momenta']);P=d['physical_propagators'];N=len(d['propagators']);ts=c['targets'];lm=d['loop_momenta'];em=d['external_momenta'];basis=label([1]*P+[0]*(N-P))
 if d.get('cut_propagators') or d.get('symbolic_ibp') or not ts:return None
 if any(len(a)!=N or any(type(v)!=int for v in a) or sum(abs(v) for v in a)>256 for a in ts):return None
 if not em and all(p['mass_squared']=='0' for p in d['propagators']):return result(c,{label(a):{} for a in ts},'scaleless_vacuum')
 if L==1 and not em and P==N==1:
  m=d['propagators'][0]['mass_squared'];rows={}
  for a in ts:rows[label(a)]={} if a[0]<1 else {basis:prod(['(d-'+str(2*j)+')/('+str(2*j)+'*'+par(m)+')' for j in range(1,a[0])])}
  return result(c,rows,'finite_tadpole')
 if P!=L+1:return None
 try:vs=[vector(p['momentum'],lm+em) for p in d['propagators']]
 except ValueError:return None
 indices=[]
 for i in range(L):
  unit=[int(j==i) for j in range(L+len(em))];hits=[j for j,v in enumerate(vs[:P]) if v in [unit,[-x for x in unit]]]
  if len(hits)!=1:return None
  indices.append(hits[0])
 tail=[j for j in range(P) if j not in indices]
 if len(tail)!=1:return None
 tail=tail[0]
 vacuum=not em and L>=2 and vs[tail] in [[1]*L,[-1]*L] and d['propagators'][tail]['mass_squared']!='0' and all(d['propagators'][j]['mass_squared']=='0' for j in indices)
 massless=len(em)==1 and vs[tail] in [[-1]*L+[1],[1]*L+[-1]] and all(p['mass_squared']=='0' for p in d['propagators'])
 if not(vacuum or massless):return None
 if any(any(v<1 for v in a[:P]) or sum(a[j]!=0 for j in range(P,N))>1 or any(a[j] not in [0,-1] for j in range(P,N)) for a in ts):return None
 if any(d['propagators'][j]['mass_squared']!='0' for a in ts for j in range(P,N) if a[j]):return None
 if vacuum:scale=d['propagators'][tail]['mass_squared']
 else:
  rules=[v for pair,v in d['scalarproduct_rules'] if pair==[em[0],em[0]]]
  if len(rules)!=1 or rules[0]=='0':return None
  scale=rules[0]
 def scalar(a,b=None):
  if any(x<1 for x in a) or (b is not None and b<1):return '0'
  A=sum(a)+(b or 0);delta=A-P
  numerator=[rf(str(P)+'-'+str(L)+'*d/2',delta)]
  denominator=[par(scale)+'**'+str(delta)]
  if vacuum:
   numerator += [str((-1)**delta),rf(str(L)+'-'+str(L-1)+'*d/2',sum(a)-L)];denominator.append(str(math.factorial(b-1)))
  else:numerator.append(rf(str(P)+'*d/2-'+str(P+delta),delta))
  for v in a:denominator += [rf('d/2-'+str(v),v-1),str(math.factorial(v-1))]
  return par(prod(numerator))+'/'+par(prod(denominator))
 rows={}
 for target in ts:
  a=[target[j] for j in indices];b=target[tail];a=a if vacuum else a+[b];active=[j for j in range(P,N) if target[j]]
  base=scalar(a,b if vacuum else None)
  if not active:value=base
  else:
   v=vs[active[0]];w=v if vacuum else [x+v[-1] for x in v[:-1]]+[v[-1]];alpha=[str(x)+'-d/2' for x in a];lam=par('+'.join(par(x) for x in alpha));terms=[]
   for i,wi in enumerate(w):
    if wi:
     shifted=list(a);shifted[i]-=1;r=scalar(shifted,b if vacuum else None)
     if r!='0':terms.append(str(wi*wi)+'*'+par(r))
   cross='+'.join(str(2*w[i]*w[j])+'*'+par(alpha[i])+'*'+par(alpha[j]) for i in range(len(w)) for j in range(i+1,len(w)) if w[i]*w[j])
   if cross:
    moment=par(cross)+'/('+lam+'*('+lam+'+d/2-1))'
    factor=par(scalar(a,b-1))+'+'+par(scale)+'*'+par(base) if vacuum else par(scale)+'*'+par(base)
    terms.append(par(moment)+'*'+par(factor))
   value='+'.join(terms) or '0'
  rows[label(target)]={} if value=='0' else {basis:value}
 return result(c,rows,'finite_one_mass_vacuum' if vacuum else 'finite_massless_propagator')
