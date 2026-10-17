"""Check routing guards and compare fresh applications with the same analytic path."""
import copy,json,os,statistics,subprocess,sys,tempfile,time
from pathlib import Path
from s01_study import HERE,ROOT,inputs,rt,make,verify,save
from s00_formula import domain,reduce as formula

def analytic_case(L,h,symbolic):
    # The analytic path needs physical denominators only, avoiding a large
    # auxiliary scalar-product basis that no calculation will use.
    names=[f'k{i+1}' for i in range(L)];p='p1';scale='q2' if symbolic else str(-2*h-29)
    den=[dict(momentum=k,mass_squared='0') for k in names]
    den.append(dict(momentum=p+'-'+ '-'.join(names),mass_squared='0'))
    ts=[]
    for i,extra in [(0,1),(L,1),(0,2)]:
        t=[1]*(L+1);t[i]+=extra
        if t not in ts:ts.append(t)
    return dict(id=f'analytic_L{L}_h{h}',size=len(ts),targets=ts,
        definition=dict(loop_momenta=names,external_momenta=[p],propagators=den,
            physical_propagators=L+1,top_level_sectors=[(1<<(L+1))-1],
            scalarproduct_rules=[[[p,p],scale]],invariants=[['q2',2]] if symbolic else []))

def guards():
    checks=[]
    for L in [1,4,8,12,32,64]:
        c=analytic_case(L,814,True);assert domain(c) is not None
        checks.append(dict(loops=L,accepted=True))
        for kind in ['mass','zero_scale','numerator','pinch','wrong_momentum','basis']:
            q=copy.deepcopy(c);basis=None
            if kind=='mass':q['definition']['propagators'][0]['mass_squared']='1'
            elif kind=='zero_scale':q['definition']['scalarproduct_rules'][0][1]='0'
            elif kind=='numerator':
                q['definition']['propagators'].append(dict(momentum='k1-p1',mass_squared='0'))
                for t in q['targets']:t.append(0)
                q['targets'][0][-1]=-1
            elif kind=='pinch':q['targets'][0][0]=0
            elif kind=='wrong_momentum':q['definition']['propagators'][0]['momentum']='2*'+q['definition']['loop_momenta'][0]
            else:basis=[q['targets'][0]]
            assert domain(q,basis) is None,(L,kind)
            checks.append(dict(loops=L,rejected=kind))
    return checks

def analytic_reference(c):
    # Independent symbolic implementation of the derived identity. It does
    # not call the live factor-cancellation routine under test.
    import sympy as sp
    info=domain(c);L=info['loops'];n=L+1;d=sp.Symbol('d');scale=sp.sympify(info['scale'],rational=True)
    master=info['master'];key=','.join(map(str,master));coeff={}
    for a in c['targets']:
        extra=[v-1 for v in a[:n]];K=sum(extra)
        value=sp.rf(n-sp.Rational(L,2)*d,K)*sp.rf(n+1-sp.Rational(n,2)*d,K)/scale**K
        for b in extra:value/=sp.rf(2-d/2,b)*sp.factorial(b)
        coeff[','.join(map(str,a))]={key:str(sp.cancel(value))}
    return dict(success=True,masters=[master],coefficients=coeff)

def boundary_checks():
    from fractions import Fraction
    import sympy as sp
    checks=[];dv=Fraction(257,101);scale=Fraction(-1657)
    for L in [1,64]:
        c=analytic_case(L,814,False);a=[1]*(L+1);a[0]=257
        c.update(targets=[a],size=1);assert domain(c) is not None
        r=formula(c);value=Fraction(1);n=L+1
        for j in range(256):value*=(n-L*dv/2+j)*(n+1-n*dv/2+j)/scale
        for j in range(256):value/=(2-dv/2+j)*(j+1)
        expr=sp.sympify(next(iter(next(iter(r['coefficients'].values())).values())),rational=True)
        actual=expr.subs(sp.Symbol('d'),sp.Rational(dv.numerator,dv.denominator))
        assert actual==sp.Rational(value.numerator,value.denominator)
        checks.append(dict(loops=L,total_extra_powers=256,exact_fraction_check=True))
        c['targets'][0][0]+=1;assert domain(c) is None
        checks.append(dict(loops=L,rejected='extra_power_limit'))
        c['targets'][0][0]=1;assert next(iter(next(iter(formula(c)['coefficients'].values())).values()))=='1'
        checks.append(dict(loops=L,corner_identity=True))
    assert domain(analytic_case(65,814,False)) is None
    checks.append(dict(loops=65,rejected='loop_limit'))
    return checks

def main():
    checks=guards()+boundary_checks()
    batch=ROOT/'ML_model_adaptive_reduction/batch_policy'
    p=rt.read(batch/'model_test/protocol.json');cases=[analytic_case(L,814,False) for L in [1,4,8,12]]
    for g in ['double_box','ladder3','nonplanar_box','massless4']:
        eligible=[c for c in p['cases'] if c['topology_group']==g and '_h721_' in c['id'] and c['shape']=='all']
        if eligible and rt.read(batch/'references'/(eligible[0]['id']+'.json.gz'))['success']:cases+=eligible[:1]
    dest=HERE/'application';protocol=dict(cases=cases,methods=['fixed_off','learned'],repetitions=3,
        analytic_path_shared=True,selection='Four predeclared analytic loop counts and the same four native application cases as the batch study.',
        formula_sha256=inputs.sha(HERE/'s00_formula.py'),route_sha256=inputs.sha(HERE/'s03_route.py'),
        batch_freeze_sha256=inputs.sha(batch/'trained_model/freeze.json'),
        batch_deployment_sha256=inputs.sha(batch/'trained_model/deployment.json'))
    protocol['application_input_fields']=['id','size','targets','definition']
    if (dest/'protocol.json').exists():assert rt.read(dest/'protocol.json')==protocol
    else:inputs.write(dest/'protocol.json',protocol)
    inputs.write(dest/'guard_checks.json',dict(passed=True,checks=checks))
    rows=[]
    for ci,c in enumerate(cases):
        info=domain(c);reference=analytic_reference(c) if info else rt.read(batch/'references'/(c['id']+'.json.gz'))
        basis=reference['masters']
        for j in range(3):
            methods=protocol['methods'];methods=methods[(ci+j)%2:]+methods[:(ci+j)%2]
            for method in methods:
                path=dest/(c['id']+'_'+method+f'_r{j}.json.gz')
                if path.exists():continue
                with tempfile.TemporaryDirectory(prefix='integral_route_',dir=os.environ['TMPDIR']) as w:
                    w=Path(w);inputs.write(w/'case.json',{k:c[k] for k in protocol['application_input_fields']});inputs.write(w/'basis.json',basis)
                    start=time.perf_counter()
                    call=subprocess.run([sys.executable,str(HERE/'s03_route.py'),'--case',str(w/'case.json'),
                         '--basis',str(w/'basis.json'),'--output',str(w/'out.json.gz'),'--strategy',method],
                         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=200)
                    assert call.returncode==0,call.stdout[-2000:]
                    r=rt.read(w/'out.json.gz')
                    if r['success']:verify(r,reference)
                    r['application_seconds']=time.perf_counter()-start;r['analytic']=bool(info)
                    if info:assert r['route']=='proven_massless_banana' and not r['learned_decision']
                    save(path,r);print('UNIFIED_APPLICATION',c['id'],method,j,r['success'],r['application_seconds'],flush=True)
        rs={m:[rt.read(dest/(c['id']+'_'+m+f'_r{j}.json.gz')) for j in range(3)] for m in protocol['methods']}
        rows.append(dict(case=c['id'],analytic=bool(info),loops=len(c['definition']['loop_momenta']),
            success=all(r['success'] for v in rs.values() for r in v),
            seconds={m:statistics.median(r['application_seconds'] for r in v) for m,v in rs.items()}))
    out=dict(complete=True,guard_checks=len(checks),all_successful_outputs_exact=True,rows=rows,
             timed=len(cases)*6,analytic_coefficients_from_proven_formula=True)
    for name,subset in [('all',[r for r in rows if r['success']]),('native',[r for r in rows if r['success'] and not r['analytic']]),('analytic',[r for r in rows if r['success'] and r['analytic']])]:
        totals={m:sum(r['seconds'][m] for r in subset) for m in protocol['methods']}
        out[name]=dict(cases=len(subset),totals=totals,ratio=totals['learned']/totals['fixed_off'] if subset else None)
    inputs.write(dest/'summary.json',out);inputs.write(ROOT/'report/integral_route_data.json',out)
    print('UNIFIED_ROUTE_COMPLETE',json.dumps(out),flush=True)

if __name__=='__main__':main()
