"""Validate a guard against the best fixed setting for each known graph."""
import json,time,statistics
from functools import lru_cache
from pathlib import Path
import s05_study as study
rt=study.rt;HERE=rt.HERE
PATH=HERE/'trained_model/graph_gate.json'

def local_features(case):
    targets=case['targets']
    return study.features(case)+[max(max(t) for t in targets),statistics.mean(sum(a>1 for a in t) for t in targets)]

@lru_cache(maxsize=16)
def _digest(path,device,inode,size,modified):
    return study.sha(path)

def file_digest(path):
    p=Path(path);s=p.stat()
    return _digest(str(p),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)

def train_graphs(cases):
    path=HERE/'trained_model/graph_candidates.json'
    if path.exists():
        d=json.loads(path.read_text());assert d['code_sha256']==study.sha(__file__)
        return d
    import numpy as np
    from sklearn.tree import DecisionTreeRegressor
    start=time.perf_counter();groups={}
    for graph in sorted({c['topology_group'] for c in cases if c['split']=='training'}):
        cs=[c for c in cases if c['split']=='training' and c['topology_group']==graph and study.available(c,'training',1)]
        if len(cs)<4:continue
        x=np.array([local_features(c) for c in cs]);t=np.array([study.times(c,'training',1) for c in cs])
        y=np.log(t/t[:,0,None]);models=[]
        for depth in [1,2,3]:
            estimator=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=2,random_state=20261015)
            estimator.fit(x,y,sample_weight=np.sqrt(t[:,0]))
            m=dict(name=graph+'_tree_'+str(depth),trees=[study.export_tree(estimator.tree_)])
            assert np.allclose(np.array([study.evaluate(m,row) for row in x]),estimator.predict(x),atol=1e-12)
            models.append(m)
        groups[graph]=dict(models=models,training_cases=[c['id'] for c in cs])
    d=dict(graphs=groups,code_sha256=study.sha(__file__),training_seconds=time.perf_counter()-start,
        features=json.loads((HERE/'trained_model/candidates.json').read_text())['features']+['max_single_power','mean_dotted_propagators'],
        candidates=sum(len(v['models']) for v in groups.values()))
    study.write(path,d);return d

def candidate_action(model,fixed,gate,case):
    scores=study.evaluate(model,local_features(case));j=min(range(len(rt.ACTIONS)),key=scores.__getitem__)
    base=rt.ACTIONS.index(fixed)
    if scores[j]>scores[base]-gate:j=base
    return rt.ACTIONS[j]

def freeze(cases,frozen):
    protocol=json.loads((HERE/'graph_control_protocol.json').read_text())
    assert protocol['test_records']==0
    for name,digest in protocol.get('source_files',{}).items():assert study.sha(HERE/name)==digest,name
    validation=[c for c in cases if c['split']=='validation' and study.available(c,'validation',2)]
    candidates=train_graphs(cases)
    graphs={}
    for graph in sorted({c['topology_group'] for c in validation}):
        cs=[c for c in validation if c['topology_group']==graph]
        totals={a:sum(study.times(c,'validation',2)[j] for c in cs) for j,a in enumerate(rt.ACTIONS)}
        fixed=min(totals,key=totals.get)
        models=[frozen['model']]+candidates['graphs'].get(graph,{}).get('models',[])
        options=[]
        for model in models:
            for gate in [0.,.05,.15]:
                cost=sum(study.times(c,'validation',2)[rt.ACTIONS.index(candidate_action(model,fixed,gate,c))] for c in cs)
                options.append(dict(model=model['name'],gate=gate,seconds=cost))
        best=min(options,key=lambda q:q['seconds']);model=next(m for m in models if m['name']==best['model'])
        learned=best['seconds'];gate=best['gate']
        repetitions=[]
        for rep in range(2):
            row={}
            for method in ['fixed','learned']:
                row[method]=sum(rt.read(HERE/'validation'/f'{c["id"]}_{fixed if method=="fixed" else candidate_action(model,fixed,gate,c)}_{rep}.json.gz')['complete_seconds'] for c in cs)
            repetitions.append(row)
        enabled=learned<=.98*totals[fixed] and all(r['learned']<r['fixed'] for r in repetitions)
        graphs[graph]=dict(fixed=fixed,enabled=enabled,fixed_seconds=totals[fixed],learned_seconds=learned,
            repetitions=repetitions,cases=[c['id'] for c in cs],candidate_totals=totals,model=model,gate=gate,options=options)
    out=dict(graphs=graphs,base_freeze_sha256=study.sha(HERE/'trained_model/freeze.json'),
        protocol_sha256=study.sha(HERE/'graph_control_protocol.json'),
        candidates_sha256=study.sha(HERE/'trained_model/graph_candidates.json'),
        code_sha256=study.sha(__file__),selection_data='validation only',minimum_saving=.02)
    if PATH.exists():assert json.loads(PATH.read_text())==out
    else:study.write(PATH,out)
    study.emit(stage='graph_guard_frozen',enabled=[g for g,v in graphs.items() if v['enabled']])
    return out

def select(frozen,guard,case):
    assert guard['base_freeze_sha256']==file_digest(HERE/'trained_model/freeze.json')
    assert guard['code_sha256']==file_digest(__file__)
    g=guard['graphs'].get(case['topology_group'])
    if g is None:return 'native'
    return candidate_action(g['model'],g['fixed'],g['gate'],case) if g['enabled'] else g['fixed']

def compare(cases,frozen,guard):
    for c in cases:
        if c['split']!='reserved':continue
        ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
        if not check.exists() or not rt.read(check)['success']:continue
        basis=rt.read(ref)['masters']
        for rep in range(3):
            methods=['graph_fixed','learned','guarded']
            for method in methods[rep:]+methods[:rep]:
                p=HERE/'graph_control_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if p.exists():continue
                start=time.perf_counter()
                if method=='graph_fixed':action=guard['graphs'][c['topology_group']]['fixed']
                elif method=='learned':action=study.select(frozen,c)
                else:action=select(frozen,guard,c)
                decision=time.perf_counter()-start
                r=rt.workflow(c,basis,action,ref)
                r.update(method=method,repetition=rep,decision_seconds=decision,complete_seconds=time.perf_counter()-start)
                rt.save(p,r);assert r['success'] and r['reference_checked']
                study.emit(stage='graph_control',case=c['id'],method=method,action=action,seconds=r['complete_seconds'])

if __name__=='__main__':
    cases=json.loads((HERE/'cases.json').read_text())['cases']
    if (HERE/'followup_cases.json').exists():cases+=json.loads((HERE/'followup_cases.json').read_text())['cases']
    frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
    compare(cases,frozen,freeze(cases,frozen))
