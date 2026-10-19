"""Complete two-point coordinates with separate development and test powers."""
from s00_prop_common import *
from fractions import Fraction
import random

def case(L,shape,profile,count=7,symbolic=True):
    names=[f'k{i+1}' for i in range(L)]+['p'];N=L*(L+1)//2+L
    def v(*items):
        a=[0]*(L+1)
        for i,x in items:a[i]+=x
        return a
    physical=[v((0,1)),v((0,1),(L,-1))]
    for j in range(1,L):
        parent=0 if shape=='star' else j-1 if shape=='chain' else (j-1)//2
        physical.extend([v((j,1)),v((j,1),(parent,-1))])
    products=[(i,j) for i in range(L) for j in range(i,L+1)];echelon={}
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
    for a in [v((i,1)) for i in range(L)]+[v((i,1),(j,-1)) for i in range(L) for j in range(i+1,L+1)]:
        if len(vectors)==N:break
        if independent(a):vectors.append(a)
    assert len(vectors)==N
    def momentum(a):return ''.join(('+' if x>0 else '-')+n for x,n in zip(a,names) if x).lstrip('+')
    P=2*L;scale='s' if symbolic else str(-2*profile-10)
    d=dict(loop_momenta=names[:L],external_momenta=['p'],propagators=[dict(momentum=momentum(v),mass_squared='0') for v in vectors],physical_propagators=P,top_level_sectors=[(1<<P)-1],scalarproduct_rules=[[['p','p'],scale]],invariants=[['s',2]] if symbolic else [],quadratic_momentum_vectors=vectors,rank=N,parameters=dict(profile=profile))
    base=[int(i<P) for i in range(N)];ts=[base]
    for i,val in [(0,2),(1,2),(P-1,2),(0,3)]:
        a=base.copy();a[i]=val
        if a not in ts:ts.append(a)
    rng=random.Random(profile*100+L)
    while len(ts)<count:
        a=[rng.randint(1,3) for _ in range(P)]+[0]*(N-P)
        if a not in ts:ts.append(a)
    name=f'propagator_tree_{shape}_L{L}_h{profile}_n{len(ts)}'
    return dict(id=name,group=name,topology_group=f'propagator_tree_{shape}_L{L}',split='reserved',definition=d,targets=ts,size=len(ts),scope='connected_propagator_tree',shape=shape,kinematics='symbolic' if symbolic else 'rational')
