"""Independent checks of saved predictions and complete finite-field trajectories."""
from s00_test_common import *
from s01_policies import pools
def main():
    cfg=test_config();results=read(TEST/"test_results.json");families=read(TEST/"family_metrics.json")
    assert results["status"]=="completed" and sha(MODEL/"trained_model.pt")==cfg["model_sha256"]
    assert read(TEST/"metric_checks.json")["status"]=="passed"
    assert results["optimizer_updates"]==0 and not results["confidence_adjustment"]
    split=read(ROOT/"ML_model_seed_selection/split_manifest.json")
    meta_by_id={f["family"]:f for f in split["families"] if f["split"]=="test"}
    assert set(families)==set(meta_by_id)
    count=collections.Counter();byloop={1:collections.Counter(),2:collections.Counter()}
    source_files={};seen_targets=set();max_model_difference=0.0
    from s05_predict import Predictor
    predictor=Predictor()
    for fid,summary in families.items():
        out=TEST/"families"/fid;meta=meta_by_id[fid];source_files.update(summary["source_hashes"])
        for name,digest in summary["artifacts"].items():assert sha(out/name)==digest
        with np.load(out/"predictions.npz",allow_pickle=False) as archive:
            z={key:archive[key] for key in archive.files}
            prob=z["probabilities"];offset=z["offsets"];targets=z["target_ids"]
            assert len(prob)==offset[-1]==len(z["action_ids"])
            assert len(z["reference"])==len(offset)-1
            for i,(lo,hi) in enumerate(zip(offset[:-1],offset[1:])):
                p=prob[lo:hi].astype(float);ref=int(z["reference"][i])
                assert np.isfinite(p).all() and np.all((p>=0)&(p<=1)) and abs(float(p.sum())-1)<2e-6
                names=z["action_ids"][lo:hi];order=np.lexsort((names,-p));pred=int(order[0])
                assert pred==z["predicted"][i] and int(pred==ref)==z["correct"][i]
                assert np.where(order==ref)[0][0]+1==z["rank"][i]
                assert p[pred]==z["confidence"][i]
                brier=float(np.sum(p*p)-2*p[ref]+1)
                assert abs(brier-z["brier"][i])<1e-10
                assert abs(-math.log(max(p[ref],1e-38))-z["nll"][i])<1e-10
                assert targets[z["target_number"][i]].startswith(fid+":")
                count["states"]+=1
                if hi-lo>1:
                    count["choices"]+=1
                    count["top3"]+=int(z["rank"][i]<=3)
                    count["top5"]+=int(z["rank"][i]<=5)
                    count["nll_sum"]+=float(z["nll"][i])
                    count["brier_sum"]+=float(z["brier"][i])
                    ties=np.flatnonzero(p==p.max())
                    metrics=dict(choice_states=1,top_tie_states=int(len(ties)>1),
                                 tie_neutral_credit=float(ref in ties)/len(ties),
                                 stable_correct=int(pred==ref))
                    count.update(metrics);byloop[meta["loops"]].update(metrics)
        base=ROOT/"integrals/testing/master_to_target/families"/fid
        identities={r["id"]:r for r in rows(base/"identities.jsonl.gz")}
        definition=read(ROOT/"integrals"/meta["definition"])
        masters={column(r["indices"]) for r in read(ROOT/"integrals"/meta["masters"])["masters"]}
        inputs={r["id"]:r for r in rows(ROOT/"integrals"/meta["inputs"])}
        refs={r["id"]:r for r in rows(ROOT/"integrals"/meta["references"])}
        n=len(definition["propagators"]);sample0=next(iter(refs.values()))["samples"][0]
        p=sample0["prime"];pool,invalid=pools(identities,masters,p,n)
        used=set()
        for record in rows(out/"trajectories.jsonl.gz"):
            tid=record["id"];assert tid not in seen_targets;seen_targets.add(tid)
            expected=clean_row(refs[tid]["samples"][0]["master_coefficients"],p,n)
            start=clean_row(inputs[tid]["modular_terms"],p,n)
            for policy in ("model","greedy"):
                saved=record[policy];current=dict(start);operations=0;trials=0
                for step in saved["path"]:
                    pivot=max((k for k in current if k not in masters),key=order_key)
                    assert pivot==step["pivot"] and step["equation"] in pool[pivot]
                    source=identities[step["equation"]]["modular_terms"];used.add(step["equation"])
                    # Independent replay uses Fermat inversion and a union expression.
                    factor=current[pivot]*pow(source[pivot],p-2,p)%p
                    after={k:(current.get(k,0)-factor*source.get(k,0))%p for k in set(current)|set(source)}
                    after={k:v for k,v in after.items() if v}
                    assert pivot not in after and len(current)==step["before_nonzeros"] and len(after)==step["after_nonzeros"]
                    cost=1+2*len(source);trial=sum(1+2*len(identities[e]["modular_terms"]) for e in pool[pivot])
                    assert cost==step["operations"] and trial==step["trial_operations"]
                    operations+=cost;trials+=trial;current=after
                    count["independent_row_replays"]+=1
                assert current==saved["final_row"] and operations==saved["operations"] and trials==saved["trial_operations"]
                assert len(saved["path"])==saved["steps"]
                assert saved["total_field_operations"]==operations+trials
                assert saved["primary_agreement"]==(current==expected)
                assert saved["success_all_samples"]==(saved["status"]=="complete" and all(s["agreement"] for s in saved["sample_checks"]))
                if saved["status"]=="complete":assert set(current)<=masters
                for sample,check in zip(refs[tid]["samples"],saved["sample_checks"]):
                    assert sample["prime"]==check["prime"]
                    if "final_row" in check:
                        answer=clean_row(sample["master_coefficients"],sample["prime"],n)
                        assert check["agreement"]==(check["final_row"]==answer)
                count[policy+"_success"]+=int(saved["success_all_samples"])
            count["targets"]+=1
        for eid in used:
            assert eval_terms(identities[eid]["terms"],sample0["point"],p)==identities[eid]["modular_terms"]
        count["used_source_rows_checked"]+=len(used)
        # Check one saved prediction per family against a fresh call to the frozen public interface.
        first_trace=next((t for t in rows(base/"elimination_traces.jsonl.gz") if t["steps"]),None)
        if first_trace:
            state=state_from_step(first_trace["steps"][0],identities,definition,masters,p)
            predicted=predictor.predict(state)
            with np.load(out/"predictions.npz",allow_pickle=False) as z:
                idx=list(z["target_ids"]).index(first_trace["id"])
                i=int(np.flatnonzero((z["target_number"]==idx)&(z["step_number"]==0))[0])
                lo,hi=z["offsets"][i:i+2]
                diff=float(np.max(np.abs(z["probabilities"][lo:hi]-np.asarray([r["probability"] for r in predicted["probabilities"]]))))
                max_model_difference=max(max_model_difference,diff);assert diff<1e-7
        parsed.cache_clear()
        write_json(TEST/"validation_status.json",dict(stage="validating",last_family=fid,targets_checked=count["targets"],states_checked=count["states"],utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())))
    for path,digest in source_files.items():assert sha(ROOT/path)==digest
    assert count["targets"]==results["targets"] and count["states"]==results["overall"]["states"]
    assert count["choices"]==results["overall"]["choice_states"]
    for policy in ("model","greedy"):assert count[policy+"_success"]==results[policy]["success_all_samples"]
    for key,numerator in (("top1","stable_correct"),("top3","top3"),("top5","top5"),("nll","nll_sum"),("brier","brier_sum")):
        assert abs(count[numerator]/count["choices"]-results["overall"][key])<1e-10
    for loop,c in byloop.items():
        assert abs(c["stable_correct"]/c["choice_states"]-results["groups"][str(loop)]["state_metrics"]["top1"])<1e-12
    tie={}
    for label,c in [("overall",count)]+[(str(k),v) for k,v in byloop.items()]:
        n=c["choice_states"]
        tie[label]=dict(choice_states=n,top_tie_states=c["top_tie_states"],
                         top_tie_fraction=c["top_tie_states"]/n if n else None,
                         tie_neutral_top1=c["tie_neutral_credit"]/n if n else None,
                         stable_top1=c["stable_correct"]/n if n else None)
    write_json(TEST/"tie_metrics.json",tie)
    final=dict(status="passed",counts=dict(count),source_files_verified=len(source_files),
               model_sha256=sha(MODEL/"trained_model.pt"),saved_model_max_probability_difference=max_model_difference,
               raw_probabilities_and_metrics_checked=True,independent_finite_field_path_replay=True,
               source_polynomials_match_stored_sample=True,held_out_family_split_verified=True,
               original_training_model_unchanged=True)
    write_json(TEST/"validation_status.json",dict(stage="passed",targets_checked=count["targets"],states_checked=count["states"]))
    write_json(TEST/"validation.json",final);print(json.dumps(final),flush=True)
if __name__=="__main__":main()
