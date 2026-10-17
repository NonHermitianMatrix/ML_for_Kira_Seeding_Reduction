"""Resolve the native basis failure before a new matched formula comparison."""
import statistics,time
from s01_study import HERE,ROOT,inputs,rt,make,verify,save
from s00_formula import reduce,domain

def measure(c,action):
    start=time.perf_counter()
    r=rt.attempt(c,[domain(c)['master']],action=action,timeout=90)
    checks=verify(r,reduce(c)) if r['success'] else 0
    return dict(case=c['id'],action=action,success=r['success'],checks=checks,
                seconds=time.perf_counter()-start,native=rt.compact(r))

def main():
    # A separate development point fixes each seed choice before the new tests.
    cases=[(L,False) for L in range(1,7)]+[(L,True) for L in range(1,5)]
    actions=['dots','native','rank_plus','expanded']
    chosen={}
    for L,symbolic in cases:
        c=make(L,810,symbolic);rows=[]
        for action in actions:
            p=HERE/'native_followup'/(c['id']+'_'+action+'.json.gz')
            if not p.exists():
                r=measure(c,action);save(p,r)
                print('BANANA_DEVELOPMENT',c['id'],action,r['success'],r['seconds'],flush=True)
            rows.append(rt.read(p))
        good=[r for r in rows if r['success']]
        chosen[str((L,symbolic))]=min(good,key=lambda r:r['seconds'])['action'] if good else None
    protocol=dict(profile=813,repetitions=3,selection=chosen,
                  selection_rule='Minimum complete development time among four fixed seed configurations.',
                  source_sha256=inputs.sha(HERE/'s04_native_followup.py'),
                  formula_sha256=inputs.sha(HERE/'s00_formula.py'),binary_sha256=inputs.sha(rt.BINARY))
    p=HERE/'native_followup/protocol.json'
    if p.exists():assert rt.read(p)==protocol
    else:inputs.write(p,protocol)
    matched=[];failed=[];checks=0
    for L,symbolic in cases:
        c=make(L,813,symbolic);action=chosen[str((L,symbolic))]
        if action is None:failed.append(c['id']);continue
        for j in range(3):
            p=HERE/'native_followup'/(c['id']+f'_r{j}.json.gz')
            if p.exists():continue
            r=measure(c,action);times=[]
            if r['success']:
                for _ in range(3):
                    start=time.perf_counter();fast=reduce(c);verify(fast,r['native'])
                    times.append(time.perf_counter()-start)
            r['formula_checked_seconds']=times;save(p,r)
            print('BANANA_RESERVED',c['id'],j,r['success'],r['seconds'],times,flush=True)
        rs=[rt.read(HERE/'native_followup'/(c['id']+f'_r{j}.json.gz')) for j in range(3)]
        checks+=sum(r['checks'] for r in rs)
        if not all(r['success'] for r in rs):failed.append(c['id']);continue
        native=statistics.median(r['seconds'] for r in rs)
        fast=statistics.median(t for r in rs for t in r['formula_checked_seconds'])
        matched.append(dict(case=c['id'],loops=L,symbolic=symbolic,action=action,
                            native_seconds=native,formula_checked_seconds=fast,speedup=native/fast))
    summary=dict(complete=True,matched=matched,failed=failed,coefficient_checks=checks,
                 learned_gain=False,all_successful_outputs_exact=True,protocol=protocol)
    inputs.write(HERE/'native_followup/summary.json',summary)
    inputs.write(ROOT/'report/massless_banana_followup_data.json',summary)
    print('BANANA_FOLLOWUP_COMPLETE',len(matched),len(failed),flush=True)

if __name__=='__main__':main()
