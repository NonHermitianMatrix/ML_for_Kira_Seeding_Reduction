"""Fit a complete-cost portfolio and compare fresh targets with the published method."""
import copy, json, math, statistics, time
from datetime import datetime, timezone
import s14_portfolio as runtime
study, rt = runtime.study, runtime.rt
HERE, ROOT, OUT, ACTIONS = runtime.HERE, runtime.ROOT, runtime.OUT, runtime.ACTIONS
features = runtime.graph.local_features

def prepare():
    old=json.loads((HERE/'cases.json').read_text())['cases']
    cases=[c for c in old if c['split']!='reserved']
    gen=study.module('portfolio_definitions',ROOT/'Kira_comparison/generalization/s01_cases.py')
    high=study.module('portfolio_higher',ROOT/'Kira_comparison/higher_scattering/s00_cases.py')
    h=306; a,b=1009+12*h,1021+14*h
    for kind in study.KINDS:
        d=copy.deepcopy(next(c['definition'] for c in old if c['topology_group']==kind))
        if kind in ['nonplanar_box','pentagon','one_mass_box']:d=gen.build(kind,False,h)
        elif kind in ['sunrise','ladder3']:
            d['scalarproduct_rules']=[[['p','p'],str(-a)]];d['parameters']['p2']=-a
        elif kind=='double_box':
            d['scalarproduct_rules']=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'-{a}/2'],[['p1','p3'],f'-{b}/2'],[['p2','p3'],f'{a+b}/2']]
            d['parameters'].update(s=-a,t=-b)
        else:
            d['propagators'][-1]['mass_squared']=str(53+2*h);d['parameters']['masses'][-1]=53+2*h
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
            cases.append(dict(id=f'{kind}_p{h}_{shape}',group=f'{kind}_p{h}',split='reserved',
                topology_group=kind,definition=d,targets=targets,size=len(targets),shape=shape))
    for loops in [3,4]:
        c=high.family('bubble_box',loops,h);c['split']='reserved';cases.append(c)
    for kind in ['nonplanar_box','pentagon','one_mass_box']:
        d=gen.build(kind,True);n=len(d['propagators']);p=d['physical_propagators']
        target=[int(i<p) for i in range(n)];target[3]+=2
        cid=f'{kind}_symbolic_portfolio'
        cases.append(dict(id=cid,group=cid,split='reserved',topology_group=kind,
            definition=d,targets=[target],size=1,shape='symbolic_dots'))
    assert len(cases)==99
    path=OUT/'protocol.json'
    scientific=['s13_previous_server.py','s14_portfolio.py','s15_portfolio_study.py']
    record=dict(cases=cases,actions=ACTIONS,training_repetitions=1,validation_repetitions=2,test_repetitions=3,
        source_hashes={n:study.sha(HERE/n) for n in scientific},
        binary_sha256=study.sha(ROOT/'.tools/kira-adaptive/kira'),
        prior_freeze_sha256=study.sha(HERE/'trained_model/graph_gate.json'),
        purpose='Compare the current learned policy, rank-only seed expansion, one or two workers, and the published workflow.',
        split='Reuse training/validation groups 301-303. Reserve new rational group 306 and symbolic dot index 3. No fitting from initial reserved group 304 or conditional group 305.',
        controls='Same exact preprocessing, master basis, two-core allocation and checks for every method. Published policy retains its existing weights; unseen bubble boxes use its native fallback.',
        guards='Enable a learned graph policy only with at least two percent validation saving and gains in both validation repetitions.',
        reference='Expanded seeds and a second rank-enlarged check. Four-loop bubble boxes use bounds [12,1,2] then [12,2,2], fixed before testing.',
        timing='Complete wall and process CPU times, including decisions, exact comparisons, cleanup and retries. Imports, reference construction and initial loading are separate.')
    if path.exists():
        stored=json.loads(path.read_text());record['registered_utc']=stored['registered_utc'];assert record==stored
    else:
        assert not list((OUT/'model_test').glob('*.gz'))
        record['registered_utc']=datetime.now(timezone.utc).isoformat();study.write(path,record)
    return cases

def reference(case):
    if case['split']!='reserved':
        p=HERE/'references'/(case['id']+'.json.gz')
        assert rt.read(p)['success'];return p
    path=OUT/'references'/(case['id']+'.json.gz')
    if not path.exists():
        custom=[12,1,2] if case['topology_group']=='bubble_box4' else rt.bounds(case,'expanded')
        r=rt.attempt(case,custom=custom,timeout=600);rt.save(path,rt.compact(r))
        study.emit(stage='portfolio_reference',case=case['id'],seconds=r['complete_seconds'],success=r['success'])
    ref=rt.read(path)
    if not ref['success']:return None
    check=path.with_name(case['id']+'_check.json.gz')
    if not check.exists():
        custom=[12,2,2] if case['topology_group']=='bubble_box4' else rt.bounds(case,'expanded')
        if case['topology_group']!='bubble_box4':custom[1]+=1
        r=rt.attempt(case,ref['masters'],reference=path,custom=custom,timeout=600)
        rt.save(check,rt.compact(r));study.emit(stage='portfolio_reference_check',case=case['id'],seconds=r['complete_seconds'],success=r['success'])
    return path if rt.read(check)['success'] else None

def measure(portfolio,cases,split,repetitions):
    for case in (c for c in cases if c['split']==split):
        ref=reference(case)
        if ref is None:continue
        basis=rt.read(ref)['masters']
        for rep in range(repetitions):
            shift=(rep+sum(case['id'].encode()))%len(ACTIONS)
            for action in ACTIONS[shift:]+ACTIONS[:shift]:
                path=OUT/split/f'{case["id"]}_{action}_{rep}.json.gz'
                if path.exists():continue
                r=portfolio.run(case,basis,action,ref);r['repetition']=rep;rt.save(path,r)
                study.emit(stage='portfolio_'+split,case=case['id'],action=action,seconds=r['complete_seconds'],success=r['success'])
                assert r['success'] and r['reference_checked']

def times(case,split,repetitions):
    return [statistics.median(rt.read(OUT/split/f'{case["id"]}_{a}_{rep}.json.gz')['complete_seconds']
        for rep in range(repetitions)) for a in ACTIONS]

def predict(model,x):
    result=[0.]*len(ACTIONS)
    for tree in model['trees']:
        i=0
        while tree['left'][i]>=0:i=tree['left'][i] if x[tree['feature'][i]]<=tree['cut'][i] else tree['right'][i]
        for j,value in enumerate(tree['value'][i]):result[j]+=value/len(model['trees'])
    return result

def choose(model,case,fixed,gate):
    scores=predict(model,features(case));idx=min(range(len(ACTIONS)),key=scores.__getitem__)
    return ACTIONS[idx] if scores[idx]<scores[ACTIONS.index(fixed)]-gate else fixed

def fit(cases):
    import numpy as np
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
    start=time.perf_counter();cs=[c for c in cases if c['split']=='training'];models=[];local={}
    def train(group,depth,kind,name):
        x=np.array([features(c) for c in group]);t=np.array([times(c,'training',1) for c in group]);y=np.log(t/t[:,0,None])
        args=dict(max_depth=depth,min_samples_leaf=2,random_state=20261016)
        estimator=DecisionTreeRegressor(**args) if kind=='tree' else (RandomForestRegressor if kind=='forest' else ExtraTreesRegressor)(n_estimators=48,n_jobs=1,**args)
        estimator.fit(x,y,sample_weight=np.sqrt(t[:,0]))
        estimators=estimator.estimators_ if hasattr(estimator,'estimators_') else [estimator]
        model=dict(name=name,trees=[study.export_tree(t.tree_) for t in estimators])
        assert np.allclose([predict(model,row) for row in x],estimator.predict(x),atol=1e-12)
        return model
    for depth in [3,5,8]:
        for kind in ['tree','forest','extra']:models.append(train(cs,depth,kind,f'{kind}_{depth}'))
    for graph in sorted({c['topology_group'] for c in cs}):
        group=[c for c in cs if c['topology_group']==graph]
        if len(group)>=4:local[graph]=[train(group,d,'tree',graph+'_tree_'+str(d)) for d in [1,2,3]]
    study.write(OUT/'trained_model/candidates.json',dict(global_models=models,local_models=local,
        training_cases=[c['id'] for c in cs],training_seconds=time.perf_counter()-start,
        features=json.loads((HERE/'trained_model/graph_candidates.json').read_text())['features'],
        objective='Weighted squared error of log complete-time ratios; weight is square root of adaptive1 cost.'))

def freeze(cases):
    candidates=json.loads((OUT/'trained_model/candidates.json').read_text());graphs={}
    for graph in sorted({c['topology_group'] for c in cases}):
        cs=[c for c in cases if c['split']=='validation' and c['topology_group']==graph]
        totals={a:sum(times(c,'validation',2)[j] for c in cs) for j,a in enumerate(ACTIONS)}
        fixed=min(totals,key=totals.get);options=[]
        models=candidates['global_models']+candidates['local_models'].get(graph,[])
        for model in models:
            for gate in [0.,.05,.15]:
                cost=sum(times(c,'validation',2)[ACTIONS.index(choose(model,c,fixed,gate))] for c in cs)
                options.append(dict(model=model['name'],gate=gate,seconds=cost))
        best=min(options,key=lambda q:q['seconds']);model=next(m for m in models if m['name']==best['model'])
        repetitions=[]
        for rep in range(2):
            row={method:sum(rt.read(OUT/'validation'/f'{c["id"]}_{fixed if method=="fixed" else choose(model,c,fixed,best["gate"])}_{rep}.json.gz')['complete_seconds'] for c in cs) for method in ['fixed','learned']}
            repetitions.append(row)
        enabled=best['seconds']<=.98*totals[fixed] and all(r['learned']<r['fixed'] for r in repetitions)
        coverage=[c for c in cases if c['split']!='reserved' and c['topology_group']==graph]
        x=list(zip(*(features(c) for c in coverage)))
        graphs[graph]=dict(fixed=fixed,enabled=enabled,model=model,gate=best['gate'],options=options,
            totals=totals,repetitions=repetitions,feature_min=list(map(min,x)),feature_max=list(map(max,x)),
            definitions=sorted({signature(c) for c in coverage}))
    out=dict(graphs=graphs,protocol_sha256=study.sha(OUT/'protocol.json'),
        candidates_sha256=study.sha(OUT/'trained_model/candidates.json'),actions=ACTIONS,
        frozen_utc=datetime.now(timezone.utc).isoformat())
    path=OUT/'trained_model/freeze.json'
    if path.exists():
        previous=json.loads(path.read_text());out['frozen_utc']=previous['frozen_utc'];assert out==previous
    else:study.write(path,out)
    study.emit(stage='portfolio_frozen',enabled=[g for g,p in graphs.items() if p['enabled']])
    return out

def signature(case):
    d=case['definition']
    return json.dumps({k:d[k] for k in ['loop_momenta','external_momenta','physical_propagators','top_level_sectors']}|{
        'momenta':[p['momentum'] for p in d['propagators']],
        'massive':[p['mass_squared']!='0' for p in d['propagators']]},sort_keys=True)

def select(frozen,case):
    graph=frozen['graphs'].get(case['topology_group'])
    if graph is None or signature(case) not in graph['definitions']:return 'native','unknown_graph'
    if any(v<lo or v>hi for v,lo,hi in zip(features(case),graph['feature_min'],graph['feature_max'])):return 'native','feature_range'
    return (choose(graph['model'],case,graph['fixed'],graph['gate']),'learned') if graph['enabled'] else (graph['fixed'],'validation_fixed')

def reduce(portfolio,case,basis,frozen):
    start=time.perf_counter();action,reason=select(frozen,case);decision=time.perf_counter()-start
    if action=='native':
        cpu0=runtime.cpu();r=portfolio.direct(case,basis,'native',1);r.update(action='native',cpu_seconds=runtime.cpu()-cpu0)
    else:r=portfolio.run(case,basis,action)
    r.update(selection_reason=reason,portfolio_decision_seconds=decision,complete_seconds=time.perf_counter()-start,
        reference_coefficients_supplied=False)
    return r

def test(portfolio,cases,frozen):
    protocol=json.loads((OUT/'protocol.json').read_text())
    for name,digest in protocol['source_hashes'].items():assert study.sha(HERE/name)==digest
    assert study.sha(OUT/'protocol.json')==frozen['protocol_sha256']
    for case in (c for c in cases if c['split']=='reserved'):
        ref=reference(case)
        if ref is None:continue
        basis=rt.read(ref)['masters'];methods=['native','adaptive','published','fixed','selected']
        for rep in range(3):
            shift=(rep+sum(case['id'].encode()))%len(methods)
            for method in methods[shift:]+methods[:shift]:
                path=OUT/'model_test'/f'{case["id"]}_{method}_{rep}.json.gz'
                if path.exists():continue
                start=time.perf_counter()
                if method=='selected':r=reduce(portfolio,case,basis,frozen)
                elif method=='native':
                    cpu0=runtime.cpu();r=portfolio.direct(case,basis,'native',1);r.update(action='native',cpu_seconds=runtime.cpu()-cpu0)
                else:
                    action='adaptive1' if method=='adaptive' else 'published' if method=='published' else frozen['graphs'][case['topology_group']]['fixed']
                    r=portfolio.run(case,basis,action)
                cpu0=runtime.cpu();rt.verify(case,r,ref);r['cpu_seconds']+=runtime.cpu()-cpu0
                r.update(method=method,repetition=rep,complete_seconds=time.perf_counter()-start)
                rt.save(path,r);study.emit(stage='portfolio_test',case=case['id'],method=method,
                    action=r['action'],seconds=r['complete_seconds'],success=r['success'])
                assert r['success'] and r['reference_checked']
        path=OUT/'applications'/(case['id']+'.json.gz')
        if not path.exists():
            r=reduce(portfolio,case,basis,frozen);rt.verify(case,r,ref);rt.save(path,r)
            assert r['success'] and r['reference_checked']

def main():
    cases=prepare();portfolio=runtime.Portfolio()
    try:
        measure(portfolio,cases,'training',1);fit(cases)
        measure(portfolio,cases,'validation',2);frozen=freeze(cases)
        test(portfolio,cases,frozen)
    finally:portfolio.close()
    study.emit(stage='portfolio_complete')

if __name__=='__main__':main()
