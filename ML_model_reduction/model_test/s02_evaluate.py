"""Frozen held-out reference-state and autonomous reduction evaluation."""
import argparse,itertools,resource
import torch
from s00_test_common import *
from s01_policies import pools,current_state,greedy_choice,rollout,sample_check

def family_evaluate(meta,predictor,cfg,sig):
    fid=meta["family"];base=ROOT/"integrals/testing/master_to_target/families"/fid
    paths={key:ROOT/"integrals"/meta[key] for key in ("definition","masters","inputs","references")}
    paths.update(identities=record_path(base/"identities.jsonl.gz"),traces=record_path(base/"elimination_traces.jsonl.gz"))
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in paths.values()}
    out=TEST/"families"/fid;out.mkdir(parents=True,exist_ok=True)
    if (out/"summary.json").exists():
        old=read(out/"summary.json")
        if old["signature"]!=sig or old["source_hashes"]!=source_hashes:raise ValueError("Changed evaluation provenance: "+fid)
        for name,digest in old["artifacts"].items():
            if sha(out/name)!=digest:raise ValueError("Changed completed artifact")
        return old
    family=read(paths["definition"])
    masters={column(m["indices"]) for m in read(paths["masters"])["masters"]}
    identities={r["id"]:r for r in rows(paths["identities"])}
    traces=list(rows(paths["traces"]));inputs=list(rows(paths["inputs"]));references=list(rows(paths["references"]))
    assert len(traces)==len(inputs)==len(references)==meta["counts"]["targets"]
    primes={t["prime"] for t in traces}
    assert len(primes)==1;prime=next(iter(primes));n=len(family["propagators"])
    pool,invalid=pools(identities,masters,prime,n)
    offsets=[0];probabilities=[];action_ids=[];target_ids=[];records=[]
    fields={k:[] for k in ("reference","predicted","rank","confidence","correct","nll","clipped_nll",
                           "brier","same_row","greedy_correct","seconds","target_number","step_number")}
    cache={};seen=set();replays=0;support_diffs=0
    for it,(target,trace,reference) in enumerate(zip(inputs,traces,references)):
        assert target["id"]==trace["id"]==reference["id"] and target["id"] not in seen
        seen.add(target["id"]);target_ids.append(target["id"])
        initial=clean_row(target["modular_terms"],prime,n)
        expected=clean_row(trace["final_master_row"],prime,n)
        assert expected==clean_row(reference["samples"][0]["master_coefficients"],prime,n)
        before=dict(initial);target_correct=[];teacher_cost=0
        for istep,step in enumerate(trace["steps"]):
            assert before==clean_row(step["before"],prime,n)
            allowed=step["allowed_pivot_equations"];pivot=column(step["pivot_indices"])
            # Establish that future rollout candidates come from the same public equation pool.
            assert set(allowed)==set(pool.get(pivot,[])),(fid,target["id"],"candidate-pool mismatch")
            state=state_from_step(step,identities,family,masters,prime)
            begin=time.perf_counter();prediction=predictor.predict(state,apply=True)
            seconds=time.perf_counter()-begin
            prob=[v["probability"] for v in prediction["probabilities"]]
            label=allowed.index(step["pivot_equation"]);metrics=classify(prob,label,allowed)
            assert prediction["selected_step"]["id"]==allowed[metrics["predicted"]]
            metrics["same_row"]=int(prediction["exact_update"]["coefficients"]==clean_row(step["after"],prime,n))
            greedy=greedy_choice(before,pivot,allowed,identities,masters,prime)
            metrics["greedy_correct"]=int(greedy==step["pivot_equation"])
            metrics.update(seconds=seconds,reference=label,target_number=it,step_number=istep)
            for k in fields:fields[k].append(metrics[k])
            probabilities.extend(prob);action_ids.extend(allowed);offsets.append(len(probabilities))
            source=identities[step["pivot_equation"]]["modular_terms"]
            after,factor=eliminate(before,source,pivot,prime)
            exact_row_check(before,source,pivot,after,prime)
            assert after==clean_row(step["after"],prime,n) and factor==step["factor_mod_p"]
            support_diffs+=int(len(before)!=step["before_nonzeros"] or len(after)!=step["after_nonzeros"])
            teacher_cost+=1+2*len(source);before=after;replays+=1
            if len(allowed)>1:target_correct.append(metrics["correct"])
        assert before==expected and set(expected)<=masters
        record=dict(id=target["id"],family=fid,loops=meta["loops"],kind=target["kind"],
                    reference_steps=len(trace["steps"]),reference_operations=teacher_cost,
                    stored_reference_operations=sum(trace["total_operations"].values()),
                    choice_states=len(target_correct),reference_choice_accuracy=float(np.mean(target_correct)) if target_correct else None,
                    all_reference_choices_match=bool(all(target_correct)) if target_correct else None)
        # Both policies receive identical initial matrix information and public equation pools.
        # Alternate their execution order by target; verification and disk I/O are outside timers.
        policies=("model","greedy") if it%2==0 else ("greedy","model")
        for policy in policies:
            result=rollout(initial,identities,pool,family,masters,prime,predictor,policy,cfg)
            result["primary_agreement"]=result["final_row"]==expected
            checks=[sample_check(target,result["path"],identities,masters,sample,cache) for sample in reference["samples"]]
            assert len(checks)==3
            result["sample_checks"]=checks
            result["success_all_samples"]=result["status"]=="complete" and all(s["agreement"] for s in checks)
            record[policy]=result
        records.append(record)
    numeric={k:np.asarray(v,dtype=np.float64 if k in ("confidence","nll","brier","seconds") else np.int32) for k,v in fields.items()}
    data=dict(numeric,offsets=np.asarray(offsets,np.int64),probabilities=np.asarray(probabilities,np.float32),
              action_ids=np.asarray(action_ids),target_ids=np.asarray(target_ids))
    write_npz(out/"predictions.npz",**data)
    write_gzip(out/"trajectories.jsonl.gz",records)
    summary=dict(family=fid,loops=meta["loops"],targets=len(records),signature=sig,source_hashes=source_hashes,
                 invalid_source_rows=invalid,reference_replays=replays,symbolic_sample_support_count_differences=support_diffs,
                 state_metrics=metric_summary(data),model=ratio_summary(records,"model"),greedy=ratio_summary(records,"greedy"),
                 artifacts={name:sha(out/name) for name in ("predictions.npz","trajectories.jsonl.gz")})
    write_json(out/"summary.json",summary)
    parsed.cache_clear()
    return summary

def aggregate(summaries,cfg,sig,seconds):
    arrays=[];records=[]
    for item in summaries:
        out=TEST/"families"/item["family"]
        with np.load(out/"predictions.npz",allow_pickle=False) as z:
            arrays.append({k:z[k] for k in z.files if k not in ("probabilities","action_ids","target_ids")})
        # Keep compact per-target records for summaries; trajectories remain in family archives.
        for r in rows(out/"trajectories.jsonl.gz"):
            for policy in ("model","greedy"):
                r[policy]={k:v for k,v in r[policy].items() if k not in ("path","final_row","sample_checks")}
            records.append(r)
    merged=merge_arrays(arrays);overall=metric_summary(merged)
    groups={}
    for loop in sorted({f["loops"] for f in summaries}):
        indexes=[i for i,f in enumerate(summaries) if f["loops"]==loop]
        if not indexes:continue
        group_records=[r for r in records if r["loops"]==loop]
        group=metric_summary(merge_arrays([arrays[i] for i in indexes]))
        groups[str(loop)]=dict(families=len(indexes),targets=len(group_records),state_metrics=group,
                              model=ratio_summary(group_records,"model"),greedy=ratio_summary(group_records,"greedy"))
    choice_targets=[r for r in records if r["choice_states"]]
    usable_families=[f["state_metrics"]["top1"] for f in summaries if f["state_metrics"]["choice_states"]]
    results=dict(status="completed",signature=sig,families=len(summaries),targets=len(records),
                 overall=overall,groups=groups,model=ratio_summary(records,"model"),greedy=ratio_summary(records,"greedy"),
                 target_mean_top1=float(np.mean([r["reference_choice_accuracy"] for r in choice_targets])),
                 all_reference_choices_fraction=float(np.mean([r["all_reference_choices_match"] for r in choice_targets])),
                 targets_with_choices=len(choice_targets),family_mean_top1=float(np.mean(usable_families)),
                 elapsed_seconds=seconds,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 weights_unchanged=sha(MODEL/"trained_model.pt")==cfg["model_sha256"],
                 optimizer_updates=0,confidence_adjustment=False,full_kira_benchmark=False,symbolic_reconstruction=False)
    held=[m for m in read(ROOT/"ML_model_seed_selection/split_manifest.json")["families"] if m["split"]=="test"]
    assert results["weights_unchanged"] and len(records)==sum(m["counts"]["targets"] for m in held) and len(summaries)==len(held)
    assert overall["states"]==sum(f["reference_replays"] for f in summaries)
    write_json(TEST/"test_results.json",results)
    write_json(TEST/"family_metrics.json",{r["family"]:r for r in summaries})
    write_gzip(TEST/"target_metrics.jsonl.gz",records)
    csv_write(TEST/"confidence_reliability.csv",overall["reliability"])
    frows=[]
    for f in summaries:
        s=f["state_metrics"]
        frows.append(dict(family=f["family"],loops=f["loops"],targets=f["targets"],states=s["states"],
            choice_states=s["choice_states"],forced_states=s["forced_states"],top1=s["top1"],top3=s["top3"],
            same_next_row=s["equivalent_next_row"],mean_confidence=s["mean_confidence"],ece=s["ece"],
            model_success=f["model"]["success_all_samples"],greedy_success=f["greedy"]["success_all_samples"],
            model_median_operation_ratio=f["model"]["median_operation_ratio"],
            model_mean_runtime_ms=f["model"]["mean_runtime_ms"],greedy_mean_runtime_ms=f["greedy"]["mean_runtime_ms"]))
    csv_write(TEST/"family_metrics.csv",frows)
    status("complete",targets=len(records),families=len(summaries),choice_states=overall["choice_states"],
           model_success=results["model"]["success_all_samples"],elapsed_seconds=seconds,max_rss_kib=results["max_rss_kib"])
    print(json.dumps(results),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--limit",type=int)
    ap.add_argument("--worker",type=int);ap.add_argument("--workers",type=int,default=1)
    ap.add_argument("--aggregate-only",action="store_true");args=ap.parse_args()
    assert args.workers>=1 and (args.worker is None or 0<=args.worker<args.workers)
    assert not (args.limit and (args.worker is not None or args.aggregate_only))
    assert not (args.aggregate_only and args.worker is not None)
    cfg=test_config();torch.set_num_threads(1);torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    assert sha(MODEL/"trained_model.pt")==cfg["model_sha256"]
    split=read(ROOT/"ML_model_seed_selection/split_manifest.json")
    train=[f for f in split["families"] if f["split"]=="train"];test=[f for f in split["families"] if f["split"]=="test"]
    assert not {f["group"] for f in train}&{f["group"] for f in test}
    # Higher-loop held-out families are evaluated first; all results use the same frozen weights.
    test.sort(key=lambda f:(-f["loops"],f["family"]))
    sig=signature();storage=storage_guard(full=True);predictor=Predictor()
    chosen=test[:args.limit] if args.limit else test
    if args.worker is not None:chosen=test[args.worker::args.workers]
    summaries=[];start=time.perf_counter()
    def progress(stage,**extra):
        if args.worker is None:status(stage,**extra)
        else:write_json(TEST/("worker_%02d_status.json"%args.worker),
             dict(stage=stage,worker=args.worker,workers=args.workers,
                  utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),**extra))
    for i,meta in enumerate(chosen):
        if args.aggregate_only:
            assert (TEST/"families"/meta["family"]/"summary.json").exists(),"Missing family test"
        result=family_evaluate(meta,predictor,cfg,sig);summaries.append(result)
        progress("checking_completed_families" if args.aggregate_only else "evaluating",families_completed=i+1,families_total=len(chosen),last_family=meta["family"],
               elapsed_seconds=time.perf_counter()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if i%64==0 or i+1==len(chosen):storage_guard()
        print("evaluated",i+1,len(chosen),meta["family"],result["state_metrics"]["top1"],result["model"]["success_all_samples"],flush=True)
    if args.limit:
        write_json(TEST/"pilot.json",dict(status="passed",signature=sig,families=[r["family"] for r in summaries],
                   elapsed_seconds=time.perf_counter()-start,full_protocol_unchanged=True))
        return
    if args.worker is not None:
        progress("complete",families_completed=len(summaries),families_total=len(chosen),
                 signature=sig,families=[r["family"] for r in summaries],elapsed_seconds=time.perf_counter()-start,
                 max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return
    elapsed=time.perf_counter()-start
    if args.aggregate_only:
        parallel=read(TEST/"parallel_execution.json")
        assert parallel["status"]=="workers_complete" and parallel["signature"]==sig
        elapsed+=parallel["elapsed_seconds"]
    aggregate(summaries,cfg,sig,elapsed)
if __name__=="__main__":main()
