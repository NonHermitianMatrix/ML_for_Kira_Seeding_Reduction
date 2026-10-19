"""Exact one-scale massless triangles, including integer numerator powers."""
from s00_batch_common import label
from s01_fast_recurrence import vector
from fractions import Fraction
import math

def product(xs):return '*'.join('('+str(x)+')' for x in xs) or '1'

def gamma_shift(z,k):
 if k>=0:return product([f'({z})+{i}' for i in range(k)])
 return '1/('+product([f'({z})-{i}' for i in range(1,1-k)])+')'

def reduce(c):
 d=c['definition'];ts=c['targets'];lm=d['loop_momenta'];em=d['external_momenta']
 if len(lm)!=1 or len(em)!=2 or len(d['propagators'])!=3:return None
 if d.get('cut_propagators') or d.get('symbolic_ibp') or any(p['mass_squared']!='0' for p in d['propagators']):return None
 if not ts or any(len(a)!=3 or any(type(v)!=int or abs(v)>16 for v in a) for a in ts):return None
 try:
  vs=[vector(p['momentum'],lm+em) for p in d['propagators']]
  if any(abs(v[0])!=1 for v in vs):return None
  shifts=[[v[j]//v[0] for j in [1,2]] for v in vs]
  rules={tuple(sorted(pair)):v for pair,v in d['scalarproduct_rules']}
  pairs=[]
  for i in range(3):
   for j in range(i+1,3):
    v=[int(shifts[i][k]-shifts[j][k]) for k in range(2)];terms=[]
    for a in range(2):
     for b in range(a,2):
      coefficient=v[a]*v[b]*(1 if a==b else 2)
      r=rules[tuple(sorted([em[a],em[b]]))]
      if coefficient and r!='0':terms.append((coefficient,r))
    if not terms:continue
    try:scale=str(sum((coefficient*Fraction(r) for coefficient,r in terms),Fraction(0)))
    except ValueError:
     # A single nonzero invariant term has a known symbolic scale.
     if len(terms)!=1:return None
     scale=f'{terms[0][0]}*({terms[0][1]})'
    if scale!='0':pairs.append((i,j,scale))
  if len(pairs)!=1:return None
 except (ValueError,KeyError):return None
 i,j,s=pairs[0];k=3-i-j;master=[0]*3;master[i]=master[j]=1;basis=label(master);rows={}
 for target in ts:
  a,b,c0=target[i],target[k],target[j]
  if a<1 or c0<1:rows[label(target)]={};continue
  total=a+b+c0;delta=total-2
  factors=[f'({s})**({-delta})',gamma_shift('2-d/2',delta),gamma_shift('d/2-1',1-a-b),gamma_shift('d/2-1',1-b-c0)]
  denominator=product([gamma_shift('d-2',-delta),math.factorial(a-1),math.factorial(c0-1)])
  rows[label(target)]={basis:'('+product(factors)+')/('+denominator+')'}
 return dict(success=True,status='completed',route='exact_one_scale_triangle',coefficients=rows,masters=[master],model_used=False,attempts=[])
