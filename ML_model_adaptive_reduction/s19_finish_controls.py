"""Finish independent controls after a bounded failure, preserving failed evidence."""
import json, os, time
from datetime import datetime, timezone
import s05_study as study
import s12_graph_policy as graph
rt=study.rt;HERE=rt.HERE;ROOT=rt.ROOT

def main():
    frozen=json.loads((HERE/'trained_model/freeze.json').read_text())
    guard=json.loads(graph.PATH.read_text());ready=json.loads((HERE/'prepared_checks.json').read_text())
    assert ready['base_freeze_sha256']==study.sha(HERE/'trained_model/freeze.json')
    assert ready['graph_gate_sha256']==study.sha(graph.PATH)
    cases=json.loads((HERE/'cases.json').read_text())['cases']
    if (HERE/'followup_cases.json').exists():cases+=json.loads((HERE/'followup_cases.json').read_text())['cases']
    selected={}
    for case in cases:
        check=HERE/'references'/(case['id']+'_check.json.gz')
        if case['split']=='reserved' and case['topology_group'] in ['bubble_box3','bubble_box4'] and check.exists() and rt.read(check)['success']:
            selected.setdefault(case['topology_group'],case)
    failed={}
    for path in (HERE/'integration_test').glob('*.gz'):
        r=rt.read(path)
        if not r['success']:
            assert all(a['status'] in ['time_limit','memory_limit','scratch_limit'] for a in r['attempts']),r
            failed[(r['case'],r['method'])]=dict(record=path.name,sha256=study.sha(path),seconds=r['complete_seconds'],
                statuses=[a['status'] for a in r['attempts']])
    assert failed,'This continuation requires a preserved bounded failure.'
    protocol=HERE/'integration_continuation.json'
    if not protocol.exists():
        study.write(protocol,dict(registered_utc=datetime.now(timezone.utc).isoformat(),
            reason='The original script stopped after saving a bounded failure. Preserve it, omit further repetitions of that failed control, and finish the other pre-specified settings.',
            original_source_sha256=study.sha(HERE/'s09_integration_check.py'),source_sha256=study.sha(__file__),
            trigger_failures={':'.join(k):v for k,v in failed.items()}))
    else:assert json.loads(protocol.read_text())['source_sha256']==study.sha(__file__)
    omitted=[]
    for case in selected.values():
        ref=HERE/'references'/(case['id']+'.json.gz');basis=rt.read(ref)['masters']
        for rep in range(3):
            methods=['previous','files','projected','learned']
            for method in methods[rep:]+methods[:rep]:
                path=HERE/'integration_test'/f'{case["id"]}_{method}_{rep}.json.gz'
                if path.exists():continue
                if (case['id'],method) in failed:
                    omitted.append(dict(case=case['id'],method=method,repetition=rep,reason='Earlier bounded failure'));continue
                start=time.perf_counter();attempts=[]
                if method=='learned':
                    action=graph.select(frozen,guard,case)
                    for choice in dict.fromkeys([action,'native','expanded']):
                        q=rt.attempt(case,basis,choice,timeout=600);attempts.append(rt.compact(q))
                        if q['success']:break
                else:
                    os.environ.update(KIRA_RUNTIME_SCRATCH='node',KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira-adaptive/kira'),
                        KIRA_EPHEMERAL_DB='1',KIRA_RESTRICT_SECTOR_INIT='1',KIRA_EQ_MODE='off',KIRA_EQ_COLLECT='0',
                        KIRA_PARALLEL_EVAL='1',KIRA_FAST_EVAL='1',KIRA_SPARSE_FEATURES='1',KIRA_ROW_PAIR_FASTPATH='1')
                    for key,on in [('KIRA_INDEX_SECTOR_FILES',method!='previous'),('KIRA_PROJECT_ZERO_CRITERION',method=='projected')]:
                        if on:os.environ[key]='1'
                        else:os.environ.pop(key,None)
                    for choice in ['native','expanded']:
                        q=rt.native.run(case,case['size'],'native',HERE/'unused',timeout=600,margin=0,
                            archive=False,records=False,basis=basis,check_masters=True,scratch_cap=32*1024**2,
                            bounds=rt.bounds(case,choice),ordering=1)
                        attempts.append(rt.compact(q))
                        if q['success']:break
                r=dict(case=case['id'],success=q['success'],coefficients=q.get('coefficients',{}),attempts=attempts,
                    fallback_count=len(attempts)-1,method=method,repetition=rep,
                    files_indexed=method!='previous',criterion_projected=method in ['projected','learned'])
                if method=='learned':r['action']=action
                rt.verify(case,r,ref);r['complete_seconds']=time.perf_counter()-start;rt.save(path,r)
                if not r['success']:
                    assert all(a['status'] in ['time_limit','memory_limit','scratch_limit'] for a in attempts),r
                    failed[(case['id'],method)]=dict(record=path.name,sha256=study.sha(path),seconds=r['complete_seconds'],
                        statuses=[a['status'] for a in attempts])
                study.emit(stage='integration_continuation',case=case['id'],method=method,seconds=r['complete_seconds'],success=r['success'])
    study.write(HERE/'integration_completion.json',dict(complete=True,omitted=omitted,
        failed_controls={':'.join(k):v for k,v in failed.items()},source_sha256=study.sha(__file__)))

if __name__=='__main__':main()
