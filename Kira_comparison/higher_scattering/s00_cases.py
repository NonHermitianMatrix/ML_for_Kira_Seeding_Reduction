"""Define connected four-point families and check their scalar-product rank."""
from fractions import Fraction
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent

def momentum(v,L):
    names=[f'k{i+1}' for i in range(L)]+['p1','p2','p3']
    s=''.join(('+' if a>0 else '-')+(str(abs(a))+'*' if abs(a)!=1 else '')+n for a,n in zip(v,names) if a)
    return s.lstrip('+')

def family(kind,L,h,symbolic=False):
    N=L*(L+1)//2+3*L
    def vec(items):
        v=[0]*(L+3)
        for i,a in items:v[i]+=a
        return v
    P=[(L,1),(L+1,1)];Q=P+[(L+2,1)]
    if kind=='ladder':
        physical=[vec([(i,1)]) for i in range(L)]+[vec([(i,1)]+[(j,-a) for j,a in P]) for i in range(L)]
        physical += [vec([(i,1),(i+1,-1)]) for i in range(L-1)]
        physical += [vec([(0,1),(L,-1)]),vec([(L-1,1)]+[(j,-a) for j,a in Q])]
    elif kind=='bubble_box':
        physical=[vec([(0,1)]),vec([(0,1),(L,-1)]),vec([(0,1)]+[(j,-a) for j,a in P]),vec([(0,1)]+[(j,-a) for j,a in Q])]
        for i in range(1,L):physical += [vec([(i,1)]),vec([(i,1),(0,-1)])]
    else:raise ValueError(kind)
    products=[(i,i) for i in range(L)]+[(i,j) for i in range(L) for j in range(i+1,L)]+[(i,j) for i in range(L) for j in range(L,L+3)]
    echelon={}
    def add(v):
        row=[Fraction(v[i]*v[j]*(1 if i==j else 2)) for i,j in products]
        for p,b in sorted(echelon.items()):
            q=row[p]
            if q:row=[a-q*c for a,c in zip(row,b)]
        pivot=next((i for i,x in enumerate(row) if x),None)
        if pivot is None:return False
        d=row[pivot];echelon[pivot]=[a/d for a in row]
        return True
    assert all(add(v) for v in physical)
    vectors=physical.copy()
    candidates=[vec([(i,1)]) for i in range(L)]+[vec([(i,1),(j,-1)]) for i in range(L) for j in range(i+1,L+3)]
    for v in candidates:
        if len(vectors)==N:break
        if add(v):vectors.append(v)
    assert len(vectors)==len(echelon)==N
    s,t=('s','t') if symbolic else (str(-1009-12*h),str(-1021-14*h))
    rules=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'({s})/2'],[['p2','p3'],f'({t})/2'],[['p1','p3'],f'-(({s})+({t}))/2']]
    n=len(physical)
    d=dict(loop_momenta=[f'k{i+1}' for i in range(L)],external_momenta=['p1','p2','p3'],
           propagators=[dict(momentum=momentum(v,L),mass_squared='0') for v in vectors],physical_propagators=n,
           top_level_sectors=[(1<<n)-1],scalarproduct_rules=rules,invariants=[['s',2],['t',2]] if symbolic else [],
           parameters=dict(s=s,t=t),rank=N,quadratic_momentum_vectors=vectors)
    corner=[1]*n+[0]*(N-n)
    dotted=corner.copy();dotted[0]=2
    numerator=corner.copy();numerator[n]=-1
    name=f'{kind}{L}_p{h}'+('_symbolic' if symbolic else '')
    return dict(id=name,group=name,topology_group=kind+str(L),split='reserved',shape='corner_dot_numerator',
                definition=d,targets=[corner,dotted,numerator],size=3,loop_coupled=True,external_points=4,
                vacuum_recurrence_applicable=False)

def main():
    cases=[family(k,L,211) for L in [4,5,6] for k in ['bubble_box','ladder']]
    cases += [family('bubble_box',4,212,True)]
    protocol=dict(cases=cases,scope='Connected massless four-point ladders and boxes with bubble subgraphs; finite representatives, not all scattering integrals.',
                  target_basis='Enlarged native reference, independently re-reduced and checked; identity-only output does not establish reduction.',
                  seed_models='Existing policies stay frozen. Unknown topology guards remain enabled.',
                  repeats=3,attempt_timeout_seconds=120,scratch_cap_bytes=16*1024**2,
                  retained_cap_bytes=2*1024**2,prior_upper_bytes=9938483200,turn_reserve_bytes=60000000,
                  combined_upper_bytes=9998483200)
    (HERE/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),dimensions=[len(c['definition']['propagators']) for c in cases])))
if __name__=='__main__':main()
