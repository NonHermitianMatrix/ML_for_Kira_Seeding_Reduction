"""Define a finite coverage grid before any new timing measurements."""
import copy, hashlib, importlib.util, json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out);return out
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def definition(kind,L,h=409,symbolic=False):
    E=0 if kind.startswith('vacuum') else 1 if kind.startswith('propagator') else 3
    names=[f'k{i+1}' for i in range(L)]+[f'p{i+1}' for i in range(E)]
    N=L*(L+1)//2+L*E
    def v(*items):
        out=[0]*(L+E)
        for i,a in items:out[i]+=a
        return out
    loop=[v((i,1)) for i in range(L)]
    if kind.startswith('vacuum'):
        physical=loop if L==1 else loop+[v(*[(i,1) for i in range(L)])]
    elif kind.startswith('propagator'):
        physical=loop+[v((L,1),*[(i,-1) for i in range(L)])]
    elif kind=='ladder':
        physical=loop+[v((i,1),(L,-1),(L+1,-1)) for i in range(L)]
        physical += [v((i,1),(i+1,-1)) for i in range(L-1)]
        physical += [v((0,1),(L,-1)),v((L-1,1),(L,-1),(L+1,-1),(L+2,-1))]
    elif kind=='bubble_box':
        physical=[v((0,1)),v((0,1),(L,-1)),v((0,1),(L,-1),(L+1,-1)),v((0,1),(L,-1),(L+1,-1),(L+2,-1))]
        for i in range(1,L):physical += [v((i,1)),v((i,1),(0,-1))]
    else:raise ValueError(kind)
    products=[(i,j) for i in range(L) for j in range(i,L)]+[(i,L+j) for i in range(L) for j in range(E)]
    echelon={}
    def add(a):
        row=[Fraction(a[i]*a[j]*(1 if i==j else 2)) for i,j in products]
        for p,b in sorted(echelon.items()):
            x=row[p]
            if x:row=[u-x*z for u,z in zip(row,b)]
        p=next((i for i,x in enumerate(row) if x),None)
        if p is None:return False
        x=row[p];echelon[p]=[z/x for z in row];return True
    assert all(add(a) for a in physical),(kind,L)
    vectors=physical.copy()
    for a in loop+[v((i,1),(j,-1)) for i in range(L) for j in range(i+1,L+E)]:
        if len(vectors)==N:break
        if add(a):vectors.append(a)
    assert len(vectors)==len(echelon)==N
    def momentum(a):
        return ''.join(('+' if x>0 else '-')+(str(abs(x))+'*' if abs(x)!=1 else '')+n for x,n in zip(a,names) if x).lstrip('+')
    p=len(physical);masses=['0']*N;invariants=[];rules=[]
    if kind=='vacuum_one_mass':masses[p-1]='m2' if symbolic else str(2*h+17)
    if kind in ['vacuum_all_mass','propagator_massive']:
        masses[:p]=[f'm{i+1}' if symbolic else str(2*h+19+6*i) for i in range(p)]
    if symbolic:invariants += [[m,2] for m in masses if m!='0']
    if E==1:
        q='q2' if symbolic else str(-2*h-29)
        rules=[[['p1','p1'],q]]
        if symbolic:invariants.append(['q2',2])
    if E==3:
        s,t=('s','t') if symbolic else (str(-1009-12*h),str(-1021-14*h))
        rules=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'({s})/2'],[['p2','p3'],f'({t})/2'],[['p1','p3'],f'-(({s})+({t}))/2']]
        if symbolic:invariants += [['s',2],['t',2]]
    return dict(loop_momenta=names[:L],external_momenta=names[L:],propagators=[dict(momentum=momentum(a),mass_squared=m) for a,m in zip(vectors,masses)],physical_propagators=p,top_level_sectors=[(1<<p)-1],scalarproduct_rules=rules,invariants=invariants,parameters=dict(profile=h),quadratic_momentum_vectors=vectors,rank=N)
def case(kind,L,symbolic=False,h=409):
    d=definition(kind,L,h,symbolic);n=len(d['propagators']);p=d['physical_propagators']
    a=[1]*p+[0]*(n-p);b=a.copy();b[0]+=1
    ts=[a,b]
    if n>p:c=a.copy();c[p]=-1;ts.append(c)
    name=f'{kind}_L{L}_h{h}'+('_symbolic' if symbolic else '')
    return dict(id=name,group=name,topology_group='coverage_'+kind+str(L),split='reserved',size=len(ts),targets=ts,definition=d,coverage_type=kind,kinematics='symbolic' if symbolic else 'rational',shape='corner_dot_numerator' if n>p else 'corner_dot')
def make():
    out=[]
    for L in range(1,13):
        for kind in ['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive','ladder','bubble_box']:
            if L==1 and kind in ['vacuum_all_mass','bubble_box']:continue
            out.append(case(kind,L))
    for kind,L in [('vacuum_one_mass',1),('propagator_massless',1),('propagator_massive',1),('propagator_massive',2),('ladder',1),('ladder',2)]:out.append(case(kind,L,True,h=410))
    gen=module('coverage_gen',ROOT/'Kira_comparison/generalization/s01_cases.py')
    for kind in ['nonplanar_box','pentagon','one_mass_box']:
        for symbolic in [False,True]:
            d=gen.build(kind,symbolic,411);p=d['physical_propagators'];n=len(d['propagators'])
            a=[int(i<p) for i in range(n)];b=a.copy();b[p-1]+=1
            name=f'{kind}_coverage_'+('symbolic' if symbolic else 'rational')
            out.append(dict(id=name,group=name,topology_group=kind,split='reserved',definition=d,targets=[a,b],size=2,coverage_type=kind,kinematics='symbolic' if symbolic else 'rational',shape='corner_dot'))
    assert len({c['id'] for c in out})==len(out)
    for c in out:
        c['loops']=len(c['definition']['loop_momenta']);n=len(c['definition']['propagators'])
        c['preflight']='eligible' if n<=31 else 'unsupported_index_count'
        c['scalar_product_count']=n
    return out
if __name__=='__main__':
    cases=make();write(HERE/'cases.json',dict(cases=cases,scope='Finite representative grid, not every graph, mass assignment, target or loop order.',loops=list(range(1,13))))
    print(json.dumps(dict(cases=len(cases),eligible=sum(c['preflight']=='eligible' for c in cases))))
