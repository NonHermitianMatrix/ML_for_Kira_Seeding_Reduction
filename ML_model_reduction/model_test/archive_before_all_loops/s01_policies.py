"""Autonomous target-row policies and exact checks at independent stored samples."""
from s00_test_common import *
def pools(identities,masters,prime,n):
    result=collections.defaultdict(list);invalid=[]
    for eid,row in identities.items():
        row["modular_terms"]=clean_row(row["modular_terms"],prime,n)
        pivot=column(row["leading_indices"])
        actual=max((k for k in row["modular_terms"] if k not in masters),key=order_key,default=None)
        if actual!=pivot or not row["modular_terms"].get(pivot):
            invalid.append(eid);continue
        result[pivot].append(eid)
    return {k:sorted(v) for k,v in result.items()},invalid
def current_state(before,pivot,allowed,identities,family,masters,prime):
    return state_from_step(dict(before=before,pivot_indices=list(indices(pivot)),allowed_pivot_equations=allowed),
                           identities,family,masters,prime)
def greedy_choice(before,pivot,allowed,identities,masters,p):
    scores=[]
    for eid in allowed:
        source=identities[eid]["modular_terms"]
        after,_=eliminate(before,source,pivot,p)
        scores.append((len(set(after)-masters),len(after),1+2*len(source),eid))
    return min(scores)[-1]
def rollout(start,identities,pool,family,masters,prime,predictor,policy,cfg):
    # Only public current-state inputs enter this function; no reference path or answer is supplied.
    before=dict(start);path=[];operations=0;trials=0;peak=len(before);state_status="step_limit"
    begin=time.perf_counter()
    for i in range(cfg["max_rollout_steps"]):
        remaining=set(before)-masters
        if not remaining:state_status="complete";break
        if len(before)>cfg["max_row_nonzeros"]:state_status="row_limit";break
        pivot=max(remaining,key=order_key);allowed=pool.get(pivot,[])
        if not allowed:state_status="no_allowed_action";break
        trial_ops=sum(1+2*len(identities[e]["modular_terms"]) for e in allowed)
        if policy=="model":
            state=current_state(before,pivot,allowed,identities,family,masters,prime)
            try:prediction=predictor.predict(state,apply=True)
            except ValueError as e:
                if "capacity exceeded" in str(e):state_status="input_limit";break
                raise
            eid=prediction["selected_step"]["id"];confidence=prediction["confidence"]
            after=prediction["exact_update"]["coefficients"]
        else:
            eid=greedy_choice(before,pivot,allowed,identities,masters,prime);confidence=None
            after,_=eliminate(before,identities[eid]["modular_terms"],pivot,prime)
        source=identities[eid]["modular_terms"]
        exact_row_check(before,source,pivot,after,prime)
        cost=1+2*len(source);operations+=cost;trials+=trial_ops
        path.append(dict(equation=eid,pivot=pivot,confidence=confidence,candidates=len(allowed),
                         before_nonzeros=len(before),after_nonzeros=len(after),operations=cost,trial_operations=trial_ops))
        before=after;peak=max(peak,len(after))
    else:
        if set(before)<=masters:state_status="complete"
    elapsed=time.perf_counter()-begin
    return dict(status=state_status,steps=len(path),operations=operations,trial_operations=trials,
                total_field_operations=operations+trials,peak_nonzeros=peak,seconds=elapsed,
                final_row=before,path=path)
def sample_check(target,path,identities,master_columns,sample,cache):
    p=sample["prime"];point=sample["point"]
    keybase=(p,tuple(sorted(point.items())))
    try:
        before=eval_terms(target["terms"],point,p)
        skipped=0
        for step in path:
            eid=step["equation"];pivot=step["pivot"]
            key=(keybase,eid)
            if key not in cache:cache[key]=eval_terms(identities[eid]["terms"],point,p)
            source=cache[key]
            if not source.get(pivot):
                return dict(status="singular_pivot",agreement=False,equation=eid,prime=p)
            if not before.get(pivot):skipped+=1;continue
            after,_=eliminate(before,source,pivot,p);exact_row_check(before,source,pivot,after,p)
            before=after
        expected={k:int(v)%p for k,v in sample["master_coefficients"].items() if int(v)%p}
        good=before==expected
        return dict(status="matched" if good else "mismatch",agreement=good,prime=p,
                    only_masters=set(before)<=master_columns,zero_target_pivots=skipped,final_row=before)
    except ZeroDivisionError:
        return dict(status="singular_coefficient",agreement=False,prime=p)
