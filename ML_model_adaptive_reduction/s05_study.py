"""Train one complete-cost policy and test it on new target and kinematic profiles."""
import copy,hashlib,importlib.util,json,math,os,re,statistics,sys,time
from pathlib import Path
import s02_runtime as rt
HERE=rt.HERE;ROOT=rt.ROOT
KINDS=['sunrise','double_box','vacuum3','ladder3','nonplanar_box','pentagon','one_mass_box']
ACTIONS=rt.ACTIONS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(**r):print(json.dumps(r),flush=True)
def write(p,r):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2)+'\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def prepare():
    old=json.loads((ROOT/'ML_model_equation_selection/early_generation/families_test.json').read_text())['cases']
    templates={c['topology_group']:c['definition'] for c in old}
    gen=module('physical_definitions',ROOT/'Kira_comparison/generalization/s01_cases.py')
    high=module('higher_definitions',ROOT/'Kira_comparison/higher_scattering/s00_cases.py')
    cases=[]
    for split,profiles in [('training',[301,302]),('validation',[303]),('reserved',[304])]:
        for h in profiles:
            for kind in KINDS:
                if kind in ['nonplanar_box','pentagon','one_mass_box']:d=gen.build(kind,False,h)
                else:
                    d=copy.deepcopy(templates[kind]);a,b=1009+12*h,1021+14*h
                    if kind in ['sunrise','ladder3']:
                        d['scalarproduct_rules']=[[['p','p'],str(-a)]];d['parameters']['p2']=-a
                    elif kind=='double_box':
                        d['scalarproduct_rules']=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'-{a}/2'],[['p1','p3'],f'-{b}/2'],[['p2','p3'],f'{a+b}/2']]
                        d['parameters'].update(s=-a,t=-b)
                    else:d['propagators'][-1]['mass_squared']=str(53+2*h);d['parameters']['masses'][-1]=53+2*h
                n=len(d['propagators']);p=d['physical_propagators'];corner=[int(i<p) for i in range(n)]
                for shape in ['dots','mixed','pinched']:
                    ts=[]
                    for j in range(3):
                        t=corner.copy();idx=(h+j)%p
                        if shape=='dots':t[idx]+=2
                        elif shape=='mixed':
                            t[idx]+=1
                            if n>p:t[p+(h+j)%(n-p)]=-1
                            else:t[(idx+1)%p]+=1
                        else:
                            t[idx]=0;t[(idx+1)%p]+=1
                        if t not in ts:ts.append(t)
                    cid=f'{kind}_p{h}_{shape}'
                    cases.append(dict(id=cid,group=f'{kind}_p{h}',split=split,topology_group=kind,
                                      definition=d,targets=ts,size=len(ts),shape=shape))
            # Connected four-point examples extend the representation to higher loops.
            # One training profile limits the cost of four-loop reference construction.
            if h!=302:
                for L in [3,4]:
                    c=high.family('bubble_box',L,h);c['split']=split;cases.append(c)
    for split,index in [('training',0),('validation',1),('reserved',2)]:
        for kind in ['nonplanar_box','pentagon','one_mass_box']:
            d=gen.build(kind,True);n=len(d['propagators']);p=d['physical_propagators']
            t=[int(i<p) for i in range(n)];t[index]+=2
            cid=f'{kind}_symbolic_{split}'
            cases.append(dict(id=cid,group=cid,split=split,topology_group=kind,definition=d,
                              targets=[t],size=1,shape='symbolic_dots'))
    record=dict(cases=cases,actions=ACTIONS,training_repetitions=1,validation_repetitions=2,test_repetitions=3,
        split_rule='Rational kinematic profiles form disjoint groups. Dot positions also change across profiles. Symbolic cases use disjoint target indices within each graph. Known graph structures; no claim of transfer to unseen graphs.',
        timing='Fresh native process and scratch for every attempt. Includes preparation, decision, exact comparison, cleanup, and fallback. References, imports, model loading and offline training are separate.',
        reference_rule='Expanded native seeds define the common basis. Reserved references receive a second enlarged-seed check.',
        memory_mib=6144,rss_mib=5200,scratch_bytes=32*1024**2,retained_bytes=64*1024**2)
    p=HERE/'cases.json'
    if p.exists():assert json.loads(p.read_text())==record
    else:write(p,record)
    emit(stage='prepared',cases=len(cases))
    return cases
def features(c):
    d=c['definition'];ts=c['targets'];lm=d['loop_momenta'];em=d['external_momenta']
    dots=[sum(max(0,a-1) for a in t) for t in ts];ranks=[sum(max(0,-a) for a in t) for t in ts]
    lines=[sum(a>0 for a in t) for t in ts];prop=d['propagators']
    incidence=[[int(re.search(r'\b'+re.escape(k)+r'\b',p['momentum']) is not None) for k in lm] for p in prop]
    physical=incidence[:d['physical_propagators']]
    return [len(lm),len(em),len(prop),d['physical_propagators'],len(d.get('invariants',[])),math.log1p(len(ts)),
        max(dots),max(ranks),statistics.mean(dots),statistics.mean(ranks),min(lines),max(lines),
        len({tuple(a>0 for a in t) for t in ts}),sum(p['mass_squared']!='0' for p in prop),
        sum(sum(v)>1 for v in physical),max(map(sum,physical)),
        max(sum(row[i] for row in physical) for i in range(len(lm))),
        sum(sum(bool(re.search(r'\b'+re.escape(k)+r'\b',p['momentum'])) for k in em) for p in prop)/len(prop)]
def reference(c):
    p=HERE/'references'/(c['id']+'.json.gz')
    if not p.exists():
        r=rt.attempt(c,action='expanded',timeout=600);rt.save(p,rt.compact(r))
        emit(stage='reference',case=c['id'],success=r['success'],status=r['status'],seconds=r['complete_seconds'])
    r=rt.read(p)
    if not r['success']:return None
    if c['split']=='reserved':
        check=HERE/'references'/(c['id']+'_check.json.gz')
        if not check.exists():
            b=rt.bounds(c,'expanded');b[1]+=1
            q=rt.attempt(c,r['masters'],reference=p,custom=b,timeout=600);rt.save(check,rt.compact(q))
            emit(stage='reference_check',case=c['id'],success=q['success'],status=q['status'],seconds=q['complete_seconds'])
        if not rt.read(check)['success']:return None
    return p
def measurements(cases,split,reps):
    for c in cases:
        if c['split']!=split:continue
        ref=reference(c)
        if ref is None:continue
        basis=rt.read(ref)['masters']
        for rep in range(reps):
            shift=(rep+sum(c['id'].encode()))%len(ACTIONS)
            for action in ACTIONS[shift:]+ACTIONS[:shift]:
                p=HERE/split/f'{c["id"]}_{action}_{rep}.json.gz'
                if p.exists():continue
                r=rt.workflow(c,basis,action,ref);r['repetition']=rep;rt.save(p,r)
                emit(stage=split,case=c['id'],action=action,success=r['success'],seconds=r['complete_seconds'],fallback=r['fallback_count'])
                assert r['success'],(c['id'],action)
def times(c,split,reps):
    return [statistics.median(rt.read(HERE/split/f'{c["id"]}_{a}_{i}.json.gz')['complete_seconds'] for i in range(reps)) for a in ACTIONS]
def available(c,split,reps):return all((HERE/split/f'{c["id"]}_{a}_{i}.json.gz').exists() for a in ACTIONS for i in range(reps))
def export_tree(t):
    return dict(left=t.children_left.tolist(),right=t.children_right.tolist(),feature=t.feature.tolist(),cut=t.threshold.tolist(),value=t.value[:,:,0].tolist())
def evaluate(model,x):
    out=[0.]*len(ACTIONS)
    for tree in model['trees']:
        i=0
        while tree['left'][i]>=0:i=tree['left'][i] if x[tree['feature'][i]]<=tree['cut'][i] else tree['right'][i]
        for j,v in enumerate(tree['value'][i]):out[j]+=v/len(model['trees'])
    return out
def train(cases):
    import numpy as np
    from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor
    cs=[c for c in cases if c['split']=='training' and available(c,'training',1)]
    x=np.array([features(c) for c in cs]);t=np.array([times(c,'training',1) for c in cs]);y=np.log(t/t[:,0,None])
    candidates=[];start=time.perf_counter()
    for depth in [3,5,8]:
        for kind in ['tree','forest','extra']:
            args=dict(max_depth=depth,min_samples_leaf=2,random_state=20261015)
            estimator=DecisionTreeRegressor(**args) if kind=='tree' else (RandomForestRegressor if kind=='forest' else ExtraTreesRegressor)(n_estimators=48,n_jobs=1,**args)
            estimator.fit(x,y,sample_weight=np.sqrt(t[:,0]))
            trees=estimator.estimators_ if hasattr(estimator,'estimators_') else [estimator]
            model=dict(name=f'{kind}_{depth}',trees=[export_tree(e.tree_) for e in trees])
            # The dependency-free production evaluator must reproduce the fitted model.
            assert np.allclose(np.array([evaluate(model,row) for row in x]),estimator.predict(x),atol=1e-12)
            candidates.append(model)
    write(HERE/'trained_model/candidates.json',dict(models=candidates,training_cases=[c['id'] for c in cs],
        features=['loops','external_momenta','indices','physical_propagators','symbolic_invariants','log_one_plus_targets','max_dots','max_rank','mean_dots','mean_rank','min_lines','max_lines','target_sectors','massive_denominators','coupled_denominators','maximum_loop_coupling','maximum_loop_incidence','mean_external_momentum_incidence'],
        actions=ACTIONS,training_seconds=time.perf_counter()-start,rows=len(cs),objective='Squared error of log complete-time ratios, weighted by square root of baseline time. Failure and recovery costs are part of every label.',
        feature_scope='Target powers and family structure. No reference coefficients, answers, timings or master labels enter prediction.'))
    emit(stage='trained',models=len(candidates),cases=len(cs),seconds=time.perf_counter()-start)
def select(f,c):
    score=evaluate(f['model'],features(c));j=min(range(len(ACTIONS)),key=score.__getitem__)
    base=ACTIONS.index(f['best_fixed'])
    if score[j]>score[base]-f['gate']:j=base
    return ACTIONS[j]
def freeze(cases):
    candidate=json.loads((HERE/'trained_model/candidates.json').read_text())
    cs=[c for c in cases if c['split']=='validation' and available(c,'validation',2)]
    totals=[sum(times(c,'validation',2)[j] for c in cs) for j in range(len(ACTIONS))]
    fixed=ACTIONS[min(range(len(ACTIONS)),key=totals.__getitem__)];options=[]
    for model in candidate['models']:
        for gate in [0.,.05,.15]:
            f=dict(model=model,best_fixed=fixed,gate=gate);cost=sum(times(c,'validation',2)[ACTIONS.index(select(f,c))] for c in cs)
            options.append(dict(model=model['name'],gate=gate,seconds=cost))
    best=min(options,key=lambda q:q['seconds']);model=next(m for m in candidate['models'] if m['name']==best['model'])
    out=dict(model=model,best_fixed=fixed,gate=best['gate'],validation=best,validation_fixed_seconds=min(totals),options=options,
        cases_sha256=sha(HERE/'cases.json'),runtime_sha256=sha(HERE/'s02_runtime.py'),study_sha256=sha(__file__),binary_sha256=sha(ROOT/'.tools/kira-adaptive/kira'),
        training_rows=candidate['rows'],validation_cases=[c['id'] for c in cs],actions=ACTIONS)
    p=HERE/'trained_model/freeze.json'
    if p.exists():assert json.loads(p.read_text())==out
    else:write(p,out)
    emit(stage='frozen',model=best['model'],gate=best['gate'],fixed=fixed,validation_seconds=best['seconds'],fixed_seconds=min(totals))
def test(cases):
    f=json.loads((HERE/'trained_model/freeze.json').read_text())
    for p,key in [(HERE/'cases.json','cases_sha256'),(HERE/'s02_runtime.py','runtime_sha256'),(Path(__file__),'study_sha256'),(ROOT/'.tools/kira-adaptive/kira','binary_sha256')]:assert sha(p)==f[key]
    for c in cases:
        if c['split']!='reserved':continue
        ref=reference(c)
        if ref is None:continue
        basis=rt.read(ref)['masters'];methods=['native','fixed','learned']
        for rep in range(3):
            for method in methods[rep:]+methods[:rep]:
                p=HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if p.exists():continue
                start=time.perf_counter();action=select(f,c) if method=='learned' else f['best_fixed'] if method=='fixed' else 'native'
                decision=time.perf_counter()-start;r=rt.workflow(c,basis,action,ref)
                r.update(method=method,repetition=rep,decision_seconds=decision,complete_seconds=time.perf_counter()-start)
                rt.save(p,r);emit(stage='test',case=c['id'],method=method,action=action,seconds=r['complete_seconds'],success=r['success'])
                assert r['success']
        # Production entry point receives the basis only; the independent comparison follows execution.
        p=HERE/'model_test'/f'{c["id"]}_application.json.gz'
        if not p.exists():
            r=rt.workflow(c,basis,select(f,c));r['answers_withheld']=True;rt.verify(c,r,ref);rt.save(p,r);assert r['success']
    emit(stage='test_complete')
def main():
    for name in ['bubble_box3_p224_parity','bubble_box4_p225_parity']:
        r=rt.read(HERE/'development'/(name+'.json.gz'))
        assert r['success'] and r['reference_checked'] and r['binary_sha256']==sha(ROOT/'.tools/kira-adaptive/kira')
    cases=prepare();measurements(cases,'training',1);train(cases);measurements(cases,'validation',2);freeze(cases);test(cases)
    emit(stage='complete')
if __name__=='__main__':main()
