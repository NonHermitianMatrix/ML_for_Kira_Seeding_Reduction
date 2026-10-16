"""Compare unchanged models with earlier or projected parametric preparation."""
import copy, json, statistics, time
from datetime import datetime,timezone
import s24_parametric_runtime as app
policy,rt,HERE,ROOT,OUT=app.policy,app.rt,app.HERE,app.ROOT,app.OUT
METHODS=['previous','native','fixed','selected']
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def prepare():
    old=json.loads((policy.OUT/'protocol.json').read_text())['cases']
    gen=policy.study.module('parametric_definitions',ROOT/'Kira_comparison/generalization/s01_cases.py')
    high=policy.study.module('parametric_higher',ROOT/'Kira_comparison/higher_scattering/s00_cases.py')
    cases=[];h=307;a,b=1009+12*h,1021+14*h
    for kind in policy.study.KINDS:
        d=copy.deepcopy(next(c['definition'] for c in old if c['topology_group']==kind))
        if kind in ['nonplanar_box','pentagon','one_mass_box']:d=gen.build(kind,False,h)
        elif kind in ['sunrise','ladder3']:
            d['scalarproduct_rules']=[[['p','p'],str(-a)]];d['parameters']['p2']=-a
        elif kind=='double_box':
            d['scalarproduct_rules']=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'-{a}/2'],[['p1','p3'],f'-{b}/2'],[['p2','p3'],f'{a+b}/2']]
            d['parameters'].update(s=-a,t=-b)
        else:d['propagators'][-1]['mass_squared']=str(53+2*h);d['parameters']['masses'][-1]=53+2*h
        n=len(d['propagators']);p=d['physical_propagators'];corner=[int(i<p) for i in range(n)]
        for shape in ['dots','mixed','pinched']:
            targets=[]
            for j in range(3):
                t=corner.copy();idx=(h+j)%p
                if shape=='dots':t[idx]+=2
                elif shape=='mixed':
                    t[idx]+=1
                    if n>p:t[p+(h+j)%(n-p)]=-1
                    else:t[(idx+1)%p]+=1
                else:t[idx]=0;t[(idx+1)%p]+=1
                if t not in targets:targets.append(t)
            cases.append(dict(id=f'{kind}_p{h}_{shape}',group=f'{kind}_p{h}',split='reserved',topology_group=kind,definition=d,targets=targets,size=len(targets),shape=shape))
    for loops in [3,4]:cases.append(high.family('bubble_box',loops,h))
    for kind in ['nonplanar_box','pentagon','one_mass_box']:
        d=gen.build(kind,True);n=len(d['propagators']);p=d['physical_propagators'];t=[int(i<p) for i in range(n)]
        if p>4:t[4]+=2
        else:t[0]+=1;t[-1]+=1
        name=kind+'_symbolic_parametric'
        cases.append(dict(id=name,group=name,split='reserved',topology_group=kind,definition=d,targets=[t],size=1,shape='symbolic_dots'))
    assert len(cases)==26
    record=dict(cases=cases,methods=METHODS,repetitions=3,
        sources={n:policy.study.sha(HERE/n) for n in ['s22_build_parametric.py','s23_parametric_runner.py','s24_parametric_runtime.py','s26_parametric_study.py']},
        model_sha256=policy.study.sha(policy.OUT/'trained_model/freeze.json'),binary_sha256=policy.study.sha(ROOT/'.tools/kira-parametric/kira'),
        old_binary_sha256=policy.study.sha(ROOT/'.tools/kira-adaptive/kira'),
        split='No fitting. Existing models stay frozen. New rational profile 307. Symbolic dot at index 4 for nonplanar/pentagon; two unit dots for virtuality box.',
        reference='Projected expanded seeds, followed by unprojected rank-enlarged seeds in the previous binary. Four-loop bounds 12,1,2 and 12,2,2.',
        timing='Same two-core job; rotated order; fresh Kira and scratch; warm models; complete wall and CPU including prediction, exact comparison, recovery, cleanup. Reference/basis construction separate.',
        changes='Early polynomial projection and bounded reuse of unchanged selected equations within one request. Same trained predictors and thresholds. The uncommon previous service remains unchanged and its costs count.')
    path=OUT/'protocol.json'
    if path.exists():assert json.loads(path.read_text())==record
    else:
        assert not list((OUT/'model_test').glob('*.gz'));write(path,record)
    return cases
def reference(c):
    ref=OUT/'references'/(c['id']+'.json.gz');check=ref.with_name(c['id']+'_check.json.gz')
    b=[12,1,2] if c['topology_group']=='bubble_box4' else rt.bounds(c,'expanded')
    if not ref.exists():
        with app.projected():r=rt.attempt(c,custom=b,timeout=600)
        rt.save(ref,rt.compact(r));emit('reference',c,r)
    assert rt.read(ref)['success'],c['id']
    if not check.exists():
        b[1]+=1;r=rt.attempt(c,rt.read(ref)['masters'],custom=b,reference=ref,timeout=600)
        rt.save(check,rt.compact(r));emit('reference_check',c,r)
    assert rt.read(check)['success'],c['id']
    return ref
def emit(stage,c,r):
    print(json.dumps(dict(stage=stage,case=c['id'],method=r.get('method'),success=r['success'],seconds=r['complete_seconds'])),flush=True)
def main():
    cases=prepare();client=app.Reducer()
    # Warm both methods equally; the independent service may be selected later.
    client.previous.portfolio.close();client.previous.portfolio=policy.runtime.Portfolio()
    try:
        for c in cases:
            ref=reference(c);basis=rt.read(ref)['masters']
            for rep in range(3):
                shift=(sum(c['id'].encode())+rep)%len(METHODS)
                for method in METHODS[shift:]+METHODS[:shift]:
                    path=OUT/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                    if path.exists():continue
                    start=time.perf_counter();cpu0=policy.runtime.cpu()
                    r=client.reduce(c,basis,method);beforecheck=policy.runtime.cpu();rt.verify(c,r,ref)
                    r['cpu_seconds']=r.get('cpu_seconds',beforecheck-cpu0)+policy.runtime.cpu()-beforecheck
                    r.update(method=method,repetition=rep,complete_seconds=time.perf_counter()-start)
                    rt.save(path,r);emit('test',c,r);assert r['success'] and r['reference_checked']
            path=OUT/'applications'/(c['id']+'.json.gz')
            if not path.exists():
                r=client.reduce(c,basis);rt.verify(c,r,ref);rt.save(path,r)
                assert r['success'] and r['reference_checked']
    finally:client.close()
    write(OUT/'completion.json',dict(complete=True,utc=datetime.now(timezone.utc).isoformat(),cases=len(cases),timings=len(cases)*len(METHODS)*3))
    print('PARAMETRIC_TEST_COMPLETE',flush=True)
if __name__=='__main__':main()
