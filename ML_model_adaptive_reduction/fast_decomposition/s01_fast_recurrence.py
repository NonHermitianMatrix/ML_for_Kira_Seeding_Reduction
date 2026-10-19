"""Exact scalar one-loop decomposition from a finite IBP matrix recurrence.

The coefficient ring is Q[d] for rational kinematics. Symbolic kinematics use
Q(x)[d]. No learned prediction or saved reduction coefficient enters this module.
"""
from fractions import Fraction
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

def inverse(matrix,one):
 n=len(matrix);a=[list(row)+[one*int(i==j) for j in range(n)] for i,row in enumerate(matrix)]
 for j in range(n):
  k=next((k for k in range(j,n) if a[k][j]),None)
  if k is None:raise Unsupported('singular sector matrix')
  a[j],a[k]=a[k],a[j];pivot=a[j][j];a[j]=[x/pivot for x in a[j]]
  for i in range(n):
   if i!=j and a[i][j]:
    c=a[i][j];a[i]=[x-c*y for x,y in zip(a[i],a[j])]
 return [row[n:] for row in a]

def reduce(case,deadline=None,pivot="largest",backend="fraction"):
 start=time.perf_counter()
 if backend=='gmp':
  import sys
  from pathlib import Path
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.tools/fast-arithmetic'))
  from gmpy2 import mpq as Rational
 else:Rational=Fraction
 d=case['definition'];ts=case['targets'];n=len(d['propagators'])
 if len(d['loop_momenta'])!=1 or not 1<=n<=5 or d['physical_propagators']!=n:return None
 if d.get('cut_propagators') or d.get('symbolic_ibp'):return None
 if not ts or any(len(a)!=n or any(type(v)!=int or v<0 for v in a) or sum(max(v-1,0) for v in a)>6 for a in ts):return None
 names=d['loop_momenta']+d['external_momenta'];E=len(names)-1
 try:
  vs=[vector(p['momentum'],names) for p in d['propagators']]
  if any(abs(v[0])!=1 for v in vs):return None
  shifts=[[x*v[0] for x in v[1:]] for v in vs]
  entries=[str(p['mass_squared']) for p in d['propagators']]+[str(v) for _,v in d['scalarproduct_rules']]
  symbolic=False
  try:values=[Rational(s) for s in entries];one=Rational(1);encode=str
  except ValueError:
   return None
  masses=values[:n];rules={tuple(sorted(pair)):v for (pair,_),v in zip(d['scalarproduct_rules'],values[n:])}
  def dot(v):
   result=one*0
   for i in range(E):
    for j in range(E):
     if v[i]*v[j]:
      key=tuple(sorted([names[i+1],names[j+1]]))
      if key not in rules:raise Unsupported('missing scalar product')
      result+=v[i]*v[j]*rules[key]
   return result
  Y=[[masses[i]+masses[j]-dot([x-y for x,y in zip(shifts[i],shifts[j])]) for j in range(n)] for i in range(n)]
  # Unit-sector masters are kept explicit. The checker independently converts
  # these into Kira's basis, including any kinematic symmetry relations.
  nodes=0;sector_inversions=0
  def trim(p):
   while p and not p[-1]:p.pop()
   return tuple(p)
  def add(row,other,scale=one,linear=None):
   for master,p in other.items():
    if linear is not None:
     q=[one*0]*(len(p)+1)
     for i,x in enumerate(p):q[i]+=linear*x;q[i+1]+=x
     p=q
    old=list(row.get(master,()));old.extend([one*0]*(len(p)-len(old)))
    for i,x in enumerate(p):old[i]+=scale*x
    v=trim(old)
    if v:row[master]=v
    else:row.pop(master,None)
  @lru_cache(None)
  def inv(sector):
   nonlocal sector_inversions
   sector_inversions+=1;return inverse([[Y[i][j] for j in sector] for i in sector],one)
  @lru_cache(None)
  def rec(a):
   nonlocal nodes
   nodes+=1
   if nodes>12000 or (deadline is not None and time.perf_counter()>deadline):raise Unsupported('analytic work limit')
   sector=tuple(i for i,v in enumerate(a) if v)
   if not sector or all(not Y[i][j] for i in sector for j in sector):return {}
   if all(v<=1 for v in a):return {a:(one,)}
   dotted=[i for i in sector if a[i]>1]
   if pivot=='largest':j=max(dotted,key=lambda i:a[i])
   elif pivot=='smallest':j=min(dotted,key=lambda i:a[i])
   elif pivot=='first':j=dotted[0]
   elif pivot=='last':j=dotted[-1]
   else:raise ValueError(pivot)
   b=list(a);b[j]-=1;b=tuple(b);B=sum(b);y=inv(sector)[sector.index(j)];result={}
   weights=[v/b[j] for v in y];total=sum(weights,one*0)
   # Collect identical integrals before multiplying polynomial rows.
   base=rec(b)
   if total:add(result,base,total,linear=-B)
   diagonal=-sum((w*b[i] for w,i in zip(weights,sector)),one*0)
   if diagonal:add(result,base,diagonal)
   for weight,i in zip(weights,sector):
    if not weight:continue
    for ell in sector:
     if ell==i:continue
     shifted=list(b);shifted[ell]+=1;shifted[i]-=1
     add(result,rec(tuple(shifted)),-weight*b[ell])
   return result
  def fmt(p):
   terms=[]
   for k,v in enumerate(p):
    if v:terms.append('('+encode(v)+')'+('*d' if k==1 else '*d**'+str(k) if k else ''))
   return '+'.join(terms) or '0'
  label=lambda a:','.join(map(str,a));rows={label(a):{label(m):fmt(v) for m,v in rec(tuple(a)).items()} for a in ts}
  masters=sorted({tuple(map(int,m.split(','))) for row in rows.values() for m in row})
  return dict(success=True,status='completed',route='one_loop_cayley_recurrence',coefficients=rows,masters=[list(a) for a in masters],model_used=False,attempts=[],analytic_seconds=time.perf_counter()-start,recurrence_states=nodes,sector_inversions=sector_inversions,symbolic_kinematics=symbolic,basis_description='Unit-power scalar sectors; additional symmetry relations can reduce this spanning set.')
 except (Unsupported,ZeroDivisionError):return None
