"""Complete scalar-product coordinates for connected rooted bubble trees."""
from s00_loop_common import *
from fractions import Fraction

def tree_case(L,shape,profile=3109,symbolic=False):
 assert shape in ['star','chain','branched']
 names=[f'k{i+1}' for i in range(L)]+['p1','p2'];N=L*(L+1)//2+2*L
 def v(*items):
  a=[0]*(L+2)
  for i,x in items:a[i]+=x
  return a
 physical=[v((0,1)),v((0,1),(L,-1)),v((0,1),(L,-1),(L+1,-1))]
 for j in range(1,L):
  parent=0 if shape=='star' else j-1 if shape=='chain' else (j-1)//2
  physical.extend([v((j,1)),v((j,1),(parent,-1))])
 products=[(i,j) for i in range(L) for j in range(i,L+2)];echelon={}
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
 for a in [v((i,1)) for i in range(L)]+[v((i,1),(j,-1)) for i in range(L) for j in range(i+1,L+2)]:
  if len(vectors)==N:break
  if independent(a):vectors.append(a)
 assert len(vectors)==N
 def momentum(a):return ''.join(('+' if x>0 else '-')+n for x,n in zip(a,names) if x).lstrip('+')
 P=len(physical);scale='s' if symbolic else str(-2*profile-10)
 d=dict(loop_momenta=names[:L],external_momenta=names[L:],propagators=[dict(momentum=momentum(v),mass_squared='0') for v in vectors],physical_propagators=P,top_level_sectors=[(1<<P)-1],scalarproduct_rules=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p1','p2'],f'({scale})/2' if symbolic else str(int(scale)//2)]],invariants=[['s',2]] if symbolic else [],quadratic_momentum_vectors=vectors,rank=N,parameters=dict(profile=profile))
 a=[int(i<P) for i in range(N)];ts=[a]
 for index,value in [(0,2),(1,0),(1,-1),(2,3),(P-1,2)]:
  b=a.copy();b[index]=value
  if b not in ts:ts.append(b)
 b=a.copy();b[0]=2;b[1]=2
 for j in range(3,P):b[j]=1+(j+profile)%2
 ts.append(b)
 name=f'bubble_tree_{shape}_L{L}_h{profile}'+('_symbolic' if symbolic else '')
 return dict(id=name,group=name,topology_group=f'bubble_tree_{shape}_L{L}',split='reserved',definition=d,targets=ts,size=len(ts),scope='connected_bubble_tree',shape=shape,kinematics='symbolic' if symbolic else 'rational')
