"""Compare complete fresh calls, retain failures, and check all returned coefficients."""
from s00_prop_common import *
from s01_propagator import reduce
from s04_prop_checks import gamma_check
import subprocess,signal,statistics,copy,shutil,sympy as sp

def measured(c,method,worker,limit):
    request=HERE/'requests'/f'case{worker}.json';output=HERE/'requests'/f'result{worker}.json.gz'
    write(request,c);start=time.perf_counter()
    proc=subprocess.Popen([sys.executable,str(HERE/'s02_runtime.py'),'--case',str(request),'--output',str(output),'--method',method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    try:
        _,err=proc.communicate(timeout=limit)
        r=read(output) if output.exists() else dict(success=False,status='missing_output')
        r['stderr_tail']=err.decode(errors='replace')[-400:]
    except subprocess.TimeoutExpired:
        # Native reductions can start independent process groups.
        old=load('prop_cleanup_runtime',TREE/'s02_runtime.py').prior();h=old.legacy().h
        helper=h.inputs.module('prop_cleanup_limits',h.BLOCK/'s11_extension_test.py')
        pids=helper.descendants(proc.pid)
        for pid in pids:
            try:os.kill(pid,signal.SIGKILL)
            except ProcessLookupError:pass
        proc.communicate();r=dict(success=False,status='application_deadline')
        for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ['TMPDIR'])]:
            for pid in pids:
                for scratch in root.glob(f'ml_kira_{pid}_*'):
                    if scratch.is_dir():shutil.rmtree(scratch)
    finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
    return r,time.perf_counter()-start

def check_prop(c,r,reference):
    if not r.get('success'):return False,0
    assert len(r['blocks'])==1
    result=r['blocks'][0]['result'];ms=result['masters']
    request=copy.deepcopy(c);request['targets']=ms;master_coeff=reduce(request)
    assert master_coeff is not None
    count=0
    for target,row in result['coefficients'].items():
        combined=sum(sp.sympify(v)*sp.sympify(next(iter(master_coeff['coefficients'][k].values()))) for k,v in row.items())
        expected=sp.sympify(next(iter(reference['coefficients'][target].values())))
        assert sp.cancel(combined-expected)==0,(c['id'],target);count+=1
    assert count==len(c['targets'])
    return True,count

def main(worker):
    p=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items())
    old=load('prop_benchmark_runtime',TREE/'s02_runtime.py').prior();h=old.legacy().h
    for i,c in enumerate(p['cases']):
        if i%2!=worker:continue
        path=HERE/'results'/(c['id']+'.json.gz')
        if path.exists():continue
        methods=['integrated','previous']+(['all_fixed'] if c['test_group']=='native' else [])
        times={m:[] for m in methods};statuses={m:[] for m in methods};success={m:[] for m in methods};checks=0;saved={};reference=None
        if c['test_group']=='propagator':reference=reduce(c);gamma=gamma_check(c,reference)
        else:gamma=dict(passed=True,checks=0)
        for rep in range(p['repetitions']):
            order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
            for method in order:
                r,seconds=measured(c,method,worker,p['seconds_per_application'])
                if r.get('success'):
                    if c['test_group']=='propagator':ok,n=check_prop(c,r,reference)
                    else:
                        if reference is None:reference=r
                        ok,n=h.compare(r,reference)
                    assert ok,(c['id'],method,'coefficient mismatch');checks+=n
                times[method].append(seconds);statuses[method].append(r.get('status'));success[method].append(bool(r.get('success')))
                saved[method]=r
        assert all(success['integrated']),(c['id'],success,statuses)
        row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),shape=c.get('shape'),targets=c['size'],times=times,
                 median_seconds={k:statistics.median(v) for k,v in times.items()},statuses=statuses,success=success,checks=checks,gamma=gamma,results=saved)
        write(path,row)
        print(json.dumps({k:v for k,v in row.items() if k in ['case','group','median_seconds','statuses','checks']}),flush=True)
    write(HERE/f'worker{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
