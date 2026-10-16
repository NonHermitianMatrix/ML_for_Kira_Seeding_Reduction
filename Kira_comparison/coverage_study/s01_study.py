"""Run matched complete reductions and supplied-basis applications on the coverage grid."""
import argparse,contextlib,gzip,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction'))
import s24_parametric_runtime as app
import s04_original_runner as original_native
from s00_cases import make,sha,write
rt=app.rt
METHODS=['full_original','full_previous','full_revised','previous','selected','native']
def save(p,d):
    raw=gzip.compress(json.dumps(d,separators=(',',':')).encode(),mtime=0)
    assert len(raw)<2*1024**2
    used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
    assert used+len(raw)<8*1024**2
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
def emit(**d):print(json.dumps(d),flush=True)
@contextlib.contextmanager
def bounded():
    original=rt.attempt
    def attempt(*args,**kw):kw['timeout']=min(kw.get('timeout',120),120);return original(*args,**kw)
    rt.attempt=attempt
    try:yield
    finally:rt.attempt=original
def bounds(c,check=False):
    p=c['definition']['physical_propagators']
    return [p+1,2 if check else 1,1]
def discover(c,revised,check=False,basis=None,ref=None):
    start=time.perf_counter()
    with app.projected() if revised else contextlib.nullcontext():
        r=rt.attempt(c,basis,custom=bounds(c,check),timeout=120)
    if ref:rt.verify(c,r,ref)
    r['complete_seconds']=time.perf_counter()-start
    return r
def original(c,ref):
    start=time.perf_counter()
    saved=dict(os.environ)
    try:
        for key in list(os.environ):
            if key.startswith('KIRA_'):os.environ.pop(key,None)
        os.environ.update(KIRA_RUNTIME_SCRATCH='node',KIRA_RUNTIME_BINARY=str(ROOT/'.tools/kira/bin/kira'))
        r=original_native.run(c,c['size'],'native',HERE/'unused',timeout=120,margin=0,archive=False,records=False,scratch_cap=32*1024**2,bounds=bounds(c),ordering=1)
    finally:
        for key in list(os.environ):
            if key.startswith('KIRA_'):os.environ.pop(key,None)
        os.environ.update({k:v for k,v in saved.items() if k.startswith('KIRA_')})
    rt.verify(c,r,ref);r['complete_seconds']=time.perf_counter()-start
    return r
def freeze(cases):
    data=dict(cases=cases,methods=METHODS,repetitions=3,attempt_seconds=120,scratch_bytes=32*1024**2,
        sources={n:sha(HERE/n) for n in ['s00_cases.py','s01_study.py','s04_original_runner.py']},
        application_sources={n:sha(ROOT/'ML_model_adaptive_reduction'/n) for n in ['s24_parametric_runtime.py','s23_parametric_runner.py','s02_runtime.py']},
        models={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'ML_model_adaptive_reduction/selective_expansion/trained_model/freeze.json',ROOT/'ML_model_adaptive_reduction/trained_model/freeze.json',ROOT/'ML_model_adaptive_reduction/trained_model/graph_gate.json']},
        binaries={n:sha(ROOT/'.tools'/n/'kira') for n in ['kira-adaptive','kira-parametric','kira/bin']},
        references='Revised expanded reduction without a prescribed basis; previous executable with numerator limit raised from one to two checks the same basis.',
        full_timing='No prescribed masters. Identical fixed expanded seeds; includes master discovery, equation generation, reduction, exact reference checks and cleanup. Exact implementation comparison; no claim of a learned gain.',
        application_timing='Supplied checked basis. Frozen previous application, revised selected application and revised native control; includes decisions, attempts, checking, recovery, cleanup. Models warm; initial loading separate.',
        failure_rule='Preserve all failures. No speedup ratio unless every paired repetition completes exactly. Unsupported index counts are not executed. No test-based policy changes.')
    p=HERE/'protocol.json'
    if p.exists():assert json.loads(p.read_text())==data
    else:write(p,data)
def process(c,client):
    if c['preflight']!='eligible':
        write(HERE/'coverage'/(c['id']+'.json'),dict(case=c['id'],status=c['preflight'],loops=c['loops'],indices=c['scalar_product_count'],timed=False));return
    ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
    if not ref.exists():
        r=discover(c,True);save(ref,rt.compact(r));emit(stage='reference',case=c['id'],status=r['status'],success=r['success'],seconds=r['complete_seconds'])
    r=rt.read(ref)
    if not r['success']:
        # Run the matched earlier attempt even when the revised reference failed.
        if not check.exists():
            old=discover(c,False);save(check,rt.compact(old));emit(stage='failed_reference_control',case=c['id'],success=old['success'],status=old['status'],seconds=old['complete_seconds'])
        write(HERE/'coverage'/(c['id']+'.json'),dict(case=c['id'],status='reference_failed',reason=r['status'],old_success=rt.read(check)['success'],timed=True));return
    nontrivial=any(row and row!={t:'1'} for t,row in r.get('coefficients',{}).items())
    basis=r['masters']
    if not check.exists():
        old=discover(c,False,check=True,basis=basis,ref=ref);save(check,rt.compact(old));emit(stage='reference_check',case=c['id'],success=old['success'],status=old['status'],seconds=old['complete_seconds'])
    old=rt.read(check)
    if not old['success']:
        write(HERE/'coverage'/(c['id']+'.json'),dict(case=c['id'],status='reference_check_failed',reason=old['status'],timed=True));return
    failed=set()
    for rep in range(3):
        shift=(sum(c['id'].encode())+rep)%len(METHODS)
        for method in METHODS[shift:]+METHODS[:shift]:
            dest=HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
            if dest.exists():
                if not rt.read(dest)['success']:failed.add(method)
                continue
            if method in failed:continue
            begin=time.perf_counter()
            if method=='full_original':result=original(c,ref)
            elif method.startswith('full_'):result=discover(c,method=='full_revised',ref=ref)
            else:
                result=client.reduce(c,basis,method);rt.verify(c,result,ref)
            result.update(case=c['id'],method=method,repetition=rep,complete_seconds=time.perf_counter()-begin)
            save(dest,rt.compact(result));emit(stage='test',case=c['id'],method=method,success=result['success'],seconds=result['complete_seconds'])
            if not result['success']:failed.add(method)
    write(HERE/'coverage'/(c['id']+'.json'),dict(case=c['id'],status='verified' if not failed else 'method_failed',failed_methods=sorted(failed),nontrivial=nontrivial,timed=True))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
    if args.pilot:
        from s00_cases import case
        cases=[case('vacuum_one_mass',2,h=401),case('propagator_massless',2,h=401),case('ladder',1,h=401)]
        for c in cases:
            c.update(loops=len(c['definition']['loop_momenta']),scalar_product_count=len(c['definition']['propagators']),preflight='eligible',split='development')
            with bounded():
                r=discover(c,True);save(HERE/'development'/(c['id']+'.json.gz'),rt.compact(r));emit(stage='pilot',case=c['id'],success=r['success'],status=r['status'])
        return
    cases=make();freeze(cases);client=app.Reducer()
    try:
        with bounded():
            for c in cases:process(c,client)
    finally:client.close()
    write(HERE/'completion.json',dict(complete=True,cases=len(cases),model_loading_seconds=client.loading_seconds))
    emit(stage='coverage_complete')
if __name__=='__main__':main()
