"""Separate native numerator batches and complete-coordinate vacuum families."""
from s00_vac_common import *
from fractions import Fraction

def native_cases(phase):
 # Patterns, rather than only invariant values, have disjoint train/validation/test assignments.
 rng=random.Random(6101);pool=[];powers=[(a,b) for a in range(5) for b in range(5-a) if 1<=a+b<=4]
 while len(pool)<48:
  n=rng.choice([1,2,2,3,4]);p=tuple(sorted(rng.sample(powers,n)))
  if p not in pool:pool.append(p)
 ranges={'training':(0,16,6011),'validation':(16,24,6029),'reserved':(24,40,6043)}
 lo,hi,profile=ranges[phase];out=[];h=batch.legacy().h
 for kind in ['double_box','nonplanar_box']:
  for i in range(lo,hi):
   c=h.inputs.case(kind,profile,'rank2',phase);ts=[[1]*7+[-a,-b] for a,b in pool[i]]
   c.update(id=f'vacml_{phase}_{kind}_p{i}',targets=ts,size=len(ts),scope='native_batch',shape='mixed_numerator_batch');out.append(batch.canonical(c))
 return out

def vacuum_case(L,shape,profile,count=7,symbolic=True):
 names=[f'k{i+1}' for i in range(L)];N=L*(L+1)//2
 def v(*items):
  a=[0]*L
  for i,x in items:a[i]+=x
  return a
 physical=[v((0,1))]
 for j in range(1,L):
  p=0 if shape=='star' else j-1 if shape=='chain' else (j-1)//2
  physical.extend([v((j,1)),v((j,1),(p,-1))])
 products=[(i,j) for i in range(L) for j in range(i,L)];echelon={}
 def independent(a):
  row=[Fraction(a[i]*a[j]*(1 if i==j else 2)) for i,j in products]
  for k,b in sorted(echelon.items()):
   x=row[k]
   if x:row=[u-x*z for u,z in zip(row,b)]
  k=next((i for i,x in enumerate(row) if x),None)
  if k is None:return False
  x=row[k];echelon[k]=[z/x for z in row];return True
 assert all(independent(a) for a in physical)
 vectors=physical.copy()
 for a in [v((i,1),(j,-1)) for i in range(L) for j in range(i+1,L)]:
  if len(vectors)==N:break
  if independent(a):vectors.append(a)
 assert len(vectors)==N
 def momentum(a):return ''.join(('+' if x>0 else '-')+n for x,n in zip(a,names) if x).lstrip('+')
 P=2*L-1;mass='m2' if symbolic else str(2*profile+11)
 d=dict(loop_momenta=names,external_momenta=[],propagators=[dict(momentum=momentum(a),mass_squared=mass if i==0 else '0') for i,a in enumerate(vectors)],physical_propagators=P,top_level_sectors=[(1<<P)-1],scalarproduct_rules=[],invariants=[['m2',2]] if symbolic else [],quadratic_momentum_vectors=vectors,rank=N,parameters=dict(profile=profile))
 base=[int(i<P) for i in range(N)];ts=[base]
 for i,val in [(0,2),(P-1,2),(0,3)]:
  a=base.copy();a[i]=val
  if a not in ts:ts.append(a)
 rng=random.Random(profile*100+L)
 if L==1:ts=[[i] for i in range(1,count+1)]
 while len(ts)<count:
  a=[rng.randint(1,3) for _ in range(P)]+[0]*(N-P)
  if a not in ts:ts.append(a)
 name=f'vacuum_tree_{shape}_L{L}_h{profile}_n{len(ts)}'
 return dict(id=name,group=name,topology_group=f'vacuum_tree_{shape}_L{L}',split='reserved',definition=d,targets=ts,size=len(ts),scope='vacuum_tree',shape=shape)
