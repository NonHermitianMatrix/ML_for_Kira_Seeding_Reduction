"""Measure complete calls, then compare exact coefficients outside the timer."""
from s00_gamma_common import *
import subprocess,signal,statistics,random,copy

def measured(c,method):
    request=HERE/'requests'/'case.json';output=HERE/'requests'/'result.json.gz'
    write(request,c)
    start=time.perf_counter()
    p=subprocess.Popen([sys.executable,str(HERE/'s02_runtime.py'),'--case',str(request),'--output',str(output),'--method',method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    try:
        _,err=p.communicate(timeout=20)
        r=read(output) if output.exists() else dict(success=False,status='missing_output')
        r['stderr_tail']=err.decode(errors='replace')[-500:]
    except subprocess.TimeoutExpired:
        os.killpg(p.pid,signal.SIGKILL);p.communicate();r=dict(success=False,status='application_deadline')
    finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
    return r,time.perf_counter()-start

def coefficients(r):return [b['result'].get('coefficients',{}) for b in r.get('blocks',[])]

def main():
    p=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items())
    check=load('gamma_cancellation_independent_check',BASE/'s07_measure.py').gamma_checks
    rows=[]
    for i,c in enumerate(p['cases']):
        path=HERE/'results'/(c['id']+'.json.gz')
        if path.exists():rows.append(read(path));continue
        times={k:[] for k in ['integrated','previous']};reference=None;checked=0;statuses=[];saved=None
        for rep in range(p['repetitions']):
            for method in (['integrated','previous'] if (i+rep)%2 else ['previous','integrated']):
                r,elapsed=measured(c,method);times[method].append(elapsed);statuses.append(r.get('status'))
                if not r.get('success'):write(HERE/'failed_request.json.gz',dict(case=c,method=method,repeat=rep,result=r,seconds=elapsed))
                assert r.get('success'),(c['id'],method,r)
                co=coefficients(r)
                if reference is None:reference=co
                assert co==reference,(c['id'],method,'coefficient mismatch')
                checked+=sum(len(x) for x in co)
                if method=='integrated':saved=r
        gamma=dict(passed=True,checks=0)
        if c['test_group']!='fallback':
            sample=copy.deepcopy(c);n=len(c['targets']);sample['targets']=[c['targets'][j] for j in sorted({0,n//2,n-1})]
            gamma=check(sample,saved)
        row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),shape=c.get('shape'),targets=len(c['targets']),times=times,
                 median_seconds={k:statistics.median(v) for k,v in times.items()},exact_coefficients_equal=True,coefficient_repeat_checks=checked,gamma=gamma,result=saved)
        write(path,row);rows.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ['result','times']}),flush=True)
    def aggregate(group):
        rr=[r for r in rows if r['group'] in group];new=sum(r['median_seconds']['integrated'] for r in rr);old=sum(r['median_seconds']['previous'] for r in rr)
        rng=random.Random(4081);ratios=[]
        for _ in range(2000):
            sample=[rng.choice(rr) for j in rr];ratios.append(sum(x['median_seconds']['integrated'] for x in sample)/sum(x['median_seconds']['previous'] for x in sample))
        ratios.sort()
        return dict(requests=len(rr),targets=sum(r['targets'] for r in rr),new_seconds=new,old_seconds=old,ratio=new/old,speedup=old/new,saving_percent=100*(1-new/old),interval=[ratios[49],ratios[1949]],slower=sum(r['median_seconds']['integrated']>r['median_seconds']['previous'] for r in rr))
    s=dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz'),groups={k:aggregate([k]) for k in ['large','small','fallback']},all=aggregate(['large','small','fallback']),analytic=aggregate(['large','small']),coefficient_repeat_checks=sum(r['coefficient_repeat_checks'] for r in rows),gamma_checks=sum(r['gamma']['checks'] for r in rows),rows=[{k:v for k,v in r.items() if k!='result'} for r in rows])
    write(HERE/'summary.json',s);print(json.dumps({k:v for k,v in s.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
