"""Repeated-pole partial fractions and analytic tadpoles in dimensional regularization.

The physical denominators use k^2-m^2+i0. Polynomial integrals and massless
vacuum integrals vanish by dimensional continuation. No numerical loop
integration or inferred coefficient enters this rule.
"""
from s00_direct_common import Q,label,ROOT,copy
import math,re,sys,time

def factors(c):
 d=c['definition'];lm=d['loop_momenta'];ps=d['propagators']
 if not 1<=len(lm)<=13 or d['external_momenta'] or d.get('cut_propagators') or d.get('symbolic_ibp') or not c['targets']:return None
 if any(len(t)!=len(ps) or any(type(a)!=int or abs(a)>8 for a in t) for t in c['targets']):return None
 indices=[]
 for k in lm:
  ids=[j for j,p in enumerate(ps) if p['momentum'].replace(' ','') in [k,'-'+k,'+'+k]]
  if not ids or len(ids)>8:return None
  indices.append(ids)
 used={i for ids in indices for i in ids}
 if any(t[j] for t in c['targets'] for j in range(len(ps)) if j not in used):return None
 try:
  masses=[Q(p['mass_squared']) for p in ps]
  if any(m<0 for m in masses):return None
 except (ValueError,ZeroDivisionError):return None
 return indices,masses

def poles(masses,a):
 """Return exact c_(mass,pole order); polynomial remainder is scaleless."""
 powers={}
 for m,n in zip(masses,a):powers[m]=powers.get(m,0)+n
 powers={m:n for m,n in powers.items() if n}
 if sum(max(n,0) for n in powers.values())>48:raise ValueError('pole work bound')
 out={}
 for x,A in powers.items():
  if A<=0:continue
  series=[Q(1)]+[Q(0)]*(A-1)
  for y,B in powers.items():
   if y==x:continue
   delta=x-y;terms=[delta**(-B)]
   for j in range(1,A):terms.append(terms[-1]*Q(-B-j+1,j)/delta)
   series=[sum((series[j]*terms[n-j] for j in range(n+1)),Q(0)) for n in range(A)]
  for n,v in enumerate(series):
   if v:out[(x,A-n)]=v
 return out

def component(c,masses):
 sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/tensor_reduction'))
 from s16_rational import K,D
 N=len(masses);rows={};raw={};masters={}
 for x in masses:
  if x:
   a=[0]*N;a[masses.index(x)]=1;masters[x]=label(a)
 for a in c['targets']:
  pp=poles(masses,a);row={};raw[label(a)]=[dict(mass_squared=str(x),pole_order=r,coefficient=str(v)) for (x,r),v in pp.items()]
  for (x,r),v in pp.items():
   if not x:continue
   ratio=K(v)
   for j in range(1,r):ratio*=((D/2-j)/(j*x))
   k=masters[x];row[k]=row.get(k,K.zero)+ratio
  rows[label(a)]={k:str(v) for k,v in row.items() if v}
 used=sorted({m for row in rows.values() for m in row});values={}
 for x,m in masters.items():
  if m in used:values[m]=dict(formula='-Gamma(1-d/2)*(mass_squared-i0)^(d/2-1)',mass_squared=str(x))
 return dict(success=True,status='completed',route='exact_vacuum_partial_fractions',coefficients=rows,masters=[list(map(int,m.split(','))) for m in used],master_values=values,partial_fractions=raw,model_used=False,attempts=[],normalization='One factor d^d k/(i*pi^(d/2)) per loop; denominators k^2-m^2+i0.')

def decompose(c):
 match=factors(c)
 if match is None:return None
 indices,masses=match;blocks=[];memo={};d=c['definition']
 try:
  for i,ids in enumerate(indices):
   ts=[list(t) for t in dict.fromkeys(tuple(t[j] for j in ids) for t in c['targets'])];sd=copy.deepcopy(d);sd['loop_momenta']=['k1'];sd['propagators']=[dict(d['propagators'][j],momentum='k1') for j in ids];sd['physical_propagators']=sum(j<d['physical_propagators'] for j in ids);sd['top_level_sectors']=[(1<<sd['physical_propagators'])-1];sd['rank']=len(ids)
   cc=dict(c,id=c['id']+'_vac'+str(i),definition=sd,targets=ts,size=len(ts));ms=[masses[j] for j in ids];key=(tuple(ms),tuple(map(tuple,ts)))
   if key not in memo:memo[key]=component(cc,ms)
   blocks.append(dict(case=cc,indices=ids,result=memo[key]))
  return dict(success=True,status='completed',blocks=blocks,model_used=False,representation='Products of explicit Gamma-function vacuum integrals in dimensional regularization.')
 except (ValueError,ZeroDivisionError,OverflowError):return None

def scaleless(c):
 """Homogeneous massless vacuum integrals vanish in dimensional regularization."""
 d=c['definition'];lm=d['loop_momenta'];ps=d['propagators'];ts=c['targets']
 if not 1<=len(lm)<=13 or d['external_momenta'] or not 1<=len(ps)<=128 or not ts or d.get('cut_propagators') or d.get('symbolic_ibp'):return None
 if any(len(a)!=len(ps) or any(type(n)!=int for n in a) for a in ts):return None
 try:
  if any(Q(p['mass_squared']) for p in ps):return None
  sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/tensor_reduction'))
  from s17_fast_tensor import vector
  vs=[vector(p['momentum'],lm) for p in ps]
  if any(not any(vs[j]) and any(a[j]>0 for a in ts) for j in range(len(ps))):return None
 except (ValueError,KeyError,SyntaxError,ZeroDivisionError):return None
 return dict(success=True,status='completed',route='exact_scaleless_vacuum',coefficients={label(a):{} for a in ts},masters=[],master_values={},analytic_value='0',analytic_evaluation_complete=True,model_used=False,attempts=[])
