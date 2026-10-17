"""Exact scalar massless banana coefficients, with a checked physical domain."""
from collections import Counter
from fractions import Fraction
from math import factorial,gcd
import re,time

def vector(text,names):
 text=text.replace(' ','');parts=text.replace('-','+-').split('+');out=[0]*len(names)
 for part in parts:
  if not part:continue
  sign=-1 if part.startswith('-') else 1;part=part.lstrip('-')
  if part not in names:raise ValueError('Momentum requires unit coefficients')
  out[names.index(part)]+=sign
 for x in out:
  if x:return tuple(v*(1 if x>0 else -1) for v in out)
 raise ValueError('Zero propagator momentum')

def domain(case,basis=None):
 d=case['definition'];lm=d['loop_momenta'];em=d['external_momenta'];L=len(lm);n=L+1;N=len(d['propagators']);ts=case['targets']
 if L<1 or L>64 or len(em)!=1 or d['physical_propagators']!=n or N<n or len(set(lm+em))!=n:return None
 if d.get('cut_propagators') or d.get('symbolic_ibp') or not ts or case['size']!=len(ts):return None
 if len(set(map(tuple,ts)))!=len(ts):return None
 expected={tuple(int(i==j) for i in range(n)) for j in range(L)}|{tuple([1]*L+[-1])}
 try:
  actual={vector(p['momentum'],lm+em) for p in d['propagators'][:n]}
  if actual!=expected or any(Fraction(p['mass_squared'])!=0 for p in d['propagators'][:n]):return None
 except (ValueError,TypeError,ZeroDivisionError):return None
 rules=d['scalarproduct_rules']
 if len(rules)!=1 or rules[0][0]!=[em[0],em[0]]:return None
 scale=str(rules[0][1])
 try:
  if Fraction(scale)==0:return None
 except ValueError:
  if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',scale) or scale=='d':return None
  if [scale,2] not in d.get('invariants',[]):return None
 master=[1]*n+[0]*(N-n)
 if basis is not None and master not in basis:return None
 for a in ts:
  if len(a)!=N or any(type(v) is not int for v in a):return None
  if any(v<1 for v in a[:n]) or any(a[n:]) or sum(v-1 for v in a[:n])>256:return None
 return dict(loops=L,physical=n,indices=N,scale=scale,master=master)

def coefficient(L,powers,scale):
 """Cancel exact linear factors before formatting; no symbolic-algebra import."""
 n=L+1;extra=[a-1 for a in powers];K=sum(extra);factors=Counter();constant=Fraction(1)
 def linear(u,v,direction):
  nonlocal constant
  g=gcd(abs(u),abs(v));sign=1 if u>0 or (u==0 and v>0) else -1
  key=(sign*u//g,sign*v//g);constant*=Fraction(sign*g,2)**direction;factors[key]+=direction
 for k in range(K):linear(-L,2*(n+k),1);linear(-n,2*(n+1+k),1)
 for k in extra:
  constant/=factorial(k)
  for j in range(k):linear(-1,2*(2+j),-1)
 symbolic=False
 try:constant/=Fraction(scale)**K
 except ValueError:symbolic=True
 def form(key):
  u,v=key;t='d' if u==1 else f'{u}*d'
  if v:t+=('+' if v>0 else '')+str(v)
  return '('+t+')'
 num=[str(constant.numerator)];den=[str(constant.denominator)] if constant.denominator!=1 else []
 for key,k in sorted(factors.items()):
  if not k:continue
  term=form(key)+(f'**{abs(k)}' if abs(k)>1 else '')
  (num if k>0 else den).append(term)
 if symbolic and K:den.append('('+scale+')'+(f'**{K}' if K>1 else ''))
 return '*'.join(num) if not den else '('+'*'.join(num)+')/('+'*'.join(den)+')'

def reduce(case,basis=None):
 start=time.perf_counter();info=domain(case,basis)
 if info is None:return None
 key=','.join(map(str,info['master']));out={','.join(map(str,a)):{key:coefficient(info['loops'],a[:info['physical']],info['scale'])} for a in case['targets']}
 return dict(case=case['id'],success=True,coefficients=out,masters=[info['master']],method='exact_massless_banana',complete_seconds=time.perf_counter()-start,reference_coefficients_supplied=False,formula_domain=info,learned_decision=False)
