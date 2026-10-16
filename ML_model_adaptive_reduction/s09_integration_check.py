"""Check public applications and separate exact preprocessing from policy gains."""
import copy,json,os,time
import s08_reduce as app
import s05_study as study
import s12_graph_policy as graph_policy
rt=study.rt;HERE=rt.HERE;ROOT=rt.ROOT
def conditional_confirmation(cases,frozen):
    original=next(c for c in cases if c['split']=='reserved' and c['topology_group']=='bubble_box4')
    check=HERE/'references'/(original['id']+'_check.json.gz')
    if check.exists() and rt.read(check)['success']:return []
    plan=json.loads((HERE/'conditional_reference_protocol.json').read_text())
    gen=study.module('conditional_family',ROOT/'Kira_comparison/higher_scattering/s00_cases.py')
    c=gen.family('bubble_box',4,plan['profile']);c['conditional_confirmation']=True
    study.write(HERE/'followup_cases.json',dict(cases=[c],reason=plan['reason'],trigger_case=original['id']))
    ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
    if not ref.exists():
        q=rt.attempt(c,custom=plan['reference_bounds'],timeout=600);rt.save(ref,rt.compact(q))
        study.emit(stage='conditional_reference',case=c['id'],success=q['success'],seconds=q['complete_seconds'])
    if not rt.read(ref)['success']:return [c]
    basis=rt.read(ref)['masters']
    if not check.exists():
        q=rt.attempt(c,basis,reference=ref,custom=plan['check_bounds'],timeout=600);rt.save(check,rt.compact(q))
        study.emit(stage='conditional_reference_check',case=c['id'],success=q['success'],seconds=q['complete_seconds'])
    if not rt.read(check)['success']:return [c]
    for rep in range(plan['repetitions']):
        methods=plan['methods']
        for method in methods[rep:]+methods[:rep]:
            out=HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
            if out.exists():continue
            start=time.perf_counter();action=study.select(frozen,c) if method=='learned' else frozen['best_fixed'] if method=='fixed' else 'native'
            decision=time.perf_counter()-start;r=rt.workflow(c,basis,action,ref)
            r.update(method=method,repetition=rep,decision_seconds=decision,complete_seconds=time.perf_counter()-start)
            rt.save(out,r);assert r['success'];study.emit(stage='conditional_test',case=c['id'],method=method,seconds=r['complete_seconds'])
    out=HERE/'model_test'/f'{c["id"]}_application.json.gz'
    if not out.exists():
        r=rt.workflow(c,basis,study.select(frozen,c));r['answers_withheld']=True;rt.verify(c,r,ref);rt.save(out,r);assert r['success']
    return [c]
def main():
    cases=json.loads((HERE/'cases.json').read_text())['cases']
    frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
    stage=os.environ.get('ADAPTIVE_CHECK_STAGE','all')
    assert stage in ['all','prepare','graph','integration']
    if stage in ['all','prepare']:
        guard=graph_policy.freeze(cases,frozen)
        cases+=conditional_confirmation(cases,frozen)
        study.write(HERE/'prepared_checks.json',dict(complete=True,base_freeze_sha256=study.sha(HERE/'trained_model/freeze.json'),
            graph_gate_sha256=study.sha(graph_policy.PATH),source_sha256=study.sha(__file__)))
        if stage=='prepare':study.emit(stage='checks_prepared');return
    else:
        ready=json.loads((HERE/'prepared_checks.json').read_text())
        assert ready['complete'] and ready['base_freeze_sha256']==study.sha(HERE/'trained_model/freeze.json')
        assert ready['graph_gate_sha256']==study.sha(graph_policy.PATH) and ready['source_sha256']==study.sha(__file__)
        guard=json.loads(graph_policy.PATH.read_text())
        if (HERE/'followup_cases.json').exists():cases+=json.loads((HERE/'followup_cases.json').read_text())['cases']
    if stage in ['all','graph']:
        graph_policy.compare(cases,frozen,guard)
        if stage=='graph':study.emit(stage='graph_controls_complete');return
    selected=[]
    for c in cases:
        if c['split']!='reserved':continue
        check=HERE/'references'/(c['id']+'_check.json.gz')
        if not check.exists() or not rt.read(check)['success']:continue
        if c['topology_group'] not in [q['topology_group'] for q in selected]:selected.append(c)
    for c in selected:
        ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
        if not check.exists() or not rt.read(check)['success']:continue
        out=HERE/'application_test'/(c['id']+'.json.gz')
        if out.exists():continue
        r=app.reduce(c,rt.read(ref)['masters'],frozen);rt.verify(c,r,ref);rt.save(out,r)
        assert r['success'];study.emit(stage='public_application',case=c['id'],action=r['action'],success=r['success'])
    if selected:
        # An unsupported graph label must keep exact native recovery available.
        c=copy.deepcopy(selected[0]);ref=HERE/'references'/(c['id']+'.json.gz')
        c['topology_group']='unsupported_application_probe'
        out=HERE/'application_test/unsupported_graph_guard.json.gz'
        if not out.exists():
            r=app.reduce(c,rt.read(ref)['masters'],frozen);rt.verify(c,r,ref)
            assert r['success'] and not r['policy_supported'] and r['action']=='native'
            rt.save(out,r);study.emit(stage='unsupported_graph_guard',success=True)
    # Fixed settings and two optional exact changes. No model refitting follows.
    for c in selected:
        if c['topology_group'] not in ['bubble_box3','bubble_box4']:continue
        ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
        if not check.exists() or not rt.read(check)['success']:continue
        basis=rt.read(ref)['masters']
        for rep in range(3):
            methods=['previous','files','projected','learned']
            for method in methods[rep:]+methods[:rep]:
                out=HERE/'integration_test'/f'{c["id"]}_{method}_{rep}.json.gz'
                if out.exists():continue
                if method=='learned':
                    start=time.perf_counter();action=graph_policy.select(frozen,guard,c)
                    attempts=[]
                    for a in dict.fromkeys([action,'native','expanded']):
                        q=rt.attempt(c,basis,a,timeout=600);attempts.append(rt.compact(q))
                        if q['success']:break
                    r=dict(case=c['id'],action=action,success=q['success'],coefficients=q.get('coefficients',{}),attempts=attempts,
                        fallback_count=len(attempts)-1,method=method,repetition=rep,files_indexed=True,criterion_projected=True)
                    rt.verify(c,r,ref);r['complete_seconds']=time.perf_counter()-start
                    rt.save(out,r);assert r['success']
                    study.emit(stage='integration_test',case=c['id'],method=method,seconds=r['complete_seconds'])
                    continue
                start=time.perf_counter()
                os.environ.update(KIRA_RUNTIME_SCRATCH='node',KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-adaptive/kira'),
                    KIRA_EPHEMERAL_DB='1',KIRA_RESTRICT_SECTOR_INIT='1',KIRA_EQ_MODE='off',KIRA_EQ_COLLECT='0',
                    KIRA_PARALLEL_EVAL='1',KIRA_FAST_EVAL='1',KIRA_SPARSE_FEATURES='1',KIRA_ROW_PAIR_FASTPATH='1')
                for key,on in [('KIRA_INDEX_SECTOR_FILES',method!='previous'),('KIRA_PROJECT_ZERO_CRITERION',method=='projected')]:
                    if on:os.environ[key]='1'
                    else:os.environ.pop(key,None)
                attempts=[]
                for action in ['native','expanded']:
                    q=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=600,margin=0,
                        archive=False,records=False,basis=basis,check_masters=True,scratch_cap=32*1024**2,
                        bounds=rt.bounds(c,action),ordering=1)
                    attempts.append(rt.compact(q))
                    if q['success']:break
                r=dict(case=c['id'],success=q['success'],coefficients=q.get('coefficients',{}),attempts=attempts,
                    fallback_count=len(attempts)-1,method=method,repetition=rep,
                    files_indexed=method!='previous',criterion_projected=method=='projected')
                rt.verify(c,r,ref);r['complete_seconds']=time.perf_counter()-start;rt.save(out,r)
                assert r['success'] and r['reference_checked'];study.emit(stage='integration_test',case=c['id'],method=method,seconds=r['complete_seconds'])
    study.emit(stage='integration_complete')
if __name__=='__main__':main()
