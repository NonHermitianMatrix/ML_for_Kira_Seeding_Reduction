"""Verify trained artifacts and write completed-training report text; no held-out evaluation."""
import collections,copy,json,resource,time
import numpy as np
import torch
from s00_common import HERE,ROOT,INTEGRALS,SPLIT,config,read,rows,sha,write_json,storage_guard,folder_size
from s01_state import column,state_from_step,encode_state,eliminate
from s05_predict import Predictor

def main():
    torch.set_num_threads(1)
    cfg=config();result=read(HERE/"trained_model.json");manifest=read(HERE/"data/manifest.json")
    checks=read(HERE/"implementation_checks.json")
    assert result["status"]=="trained_testing_deferred" and checks["status"]=="passed"
    assert result["epochs_completed"]==cfg["epochs"]==10
    assert result["model_sha256"]==sha(HERE/"trained_model.pt")
    assert result["fingerprint"]["manifest_sha256"]==sha(HERE/"data/manifest.json")
    assert manifest["split_sha256"]==sha(SPLIT)
    assert manifest["preparation_signature"]["encoder_sha256"]==sha(HERE/"s01_state.py")
    model=torch.load(HERE/"trained_model.pt",map_location="cpu",weights_only=False)
    latest=torch.load(HERE/"runs/latest.pt",map_location="cpu",weights_only=False)
    assert latest["epoch"]==cfg["epochs"] and latest["next_group"]==0
    assert latest["history"]==result["history"]
    assert all(torch.equal(v,latest["model"][k]) and torch.isfinite(v).all() for k,v in model["model"].items())
    assert result["choice_state_presentations"]==manifest["counts"]["choice_states"]*cfg["epochs"]
    assert len(result["history"])==cfg["epochs"]
    counts=collections.Counter();source_hashes={};max_actions=0
    for family in manifest["families"]:
        path=HERE/family["file"];assert sha(path)==family["sha256"]
        source_hashes.update(family["source_hashes"])
        with np.load(path,allow_pickle=False) as z:
            features=z["features"];offsets=z["offsets"];labels=z["labels"]
            n=np.diff(offsets)
            assert features.dtype==np.float32 and np.isfinite(features).all()
            assert features.shape==(int(offsets[-1]),manifest["feature_dim"])
            assert offsets[0]==0 and np.all(n>=1) and np.all((labels>=0)&(labels<n))
            assert len(z["target_number"])==len(labels)==len(z["step_number"])
            assert len(z["action_ids"])==len(features)
            assert np.all(z["target_number"]>=0) and np.all(z["target_number"]<len(z["target_ids"]))
            counts["states"]+=len(labels);counts["choice_states"]+=int((n>1).sum())
            counts["forced_states"]+=int((n==1).sum());counts["candidate_actions"]+=len(features)
            counts["targets"]+=len(z["target_ids"])
            max_actions=max(max_actions,int(n.max(initial=0)))
    for k,v in counts.items():assert manifest["counts"][k]==v
    for path,digest in source_hashes.items():assert sha(INTEGRALS/path)==digest
    # Ensure the completed seed model remains unchanged.
    seed_hash=sha(ROOT/"ML_model_seed_selection/trained_model.pt")
    assert seed_hash=="931ec67c287af4edbea3e6525e2cc1f8a95e04f164c24d262855986e44c3f589"
    family=manifest["families"][0]["family"]
    meta=next(f for f in read(SPLIT)["families"] if f["family"]==family)
    base=INTEGRALS/"training/master_to_target/families"/family
    definition=read(INTEGRALS/meta["definition"])
    masters={column(x["indices"]) for x in read(INTEGRALS/meta["masters"])["masters"]}
    trace,step_index=next((t,i) for t in rows(base/"elimination_traces.jsonl.gz")
                          for i,s in enumerate(t["steps"]) if len(s["allowed_pivot_equations"])>1)
    step=trace["steps"][step_index];wanted=set(step["allowed_pivot_equations"])
    identities={r["id"]:r for r in rows(base/"identities.jsonl.gz") if r["id"] in wanted}
    state=state_from_step(step,identities,definition,masters,trace["prime"])
    encoded=encode_state(state,cfg)
    with np.load(HERE/manifest["families"][0]["file"],allow_pickle=False) as z:
        target_idx=list(z["target_ids"]).index(trace["id"])
        i=int(np.flatnonzero((z["target_number"]==target_idx)&(z["step_number"]==step_index))[0])
        lo,hi=z["offsets"][i:i+2]
        assert np.array_equal(z["features"][lo:hi],encoded)
    predictor=Predictor();prediction=predictor.predict(state,apply=True)
    probs={o["step"]["id"]:o["probability"] for o in prediction["probabilities"]}
    assert abs(sum(probs.values())-1)<1e-6
    assert prediction["confidence"]==max(probs.values())
    selected=prediction["selected_step"]
    after,_=eliminate(state["rows"][selected["destination_row"]],
                      state["rows"][selected["source_row"]],column(selected["pivot_indices"]),state["prime"])
    assert prediction["exact_update"]["coefficients"]==after
    # Independent cross-multiplication avoids using the row-update implementation as its own oracle.
    src=state["rows"][selected["source_row"]];dst=state["rows"][selected["destination_row"]]
    pivot=column(selected["pivot_indices"]);prime=state["prime"]
    for key in set(src)|set(dst)|set(after):
        assert after.get(key,0)*src[pivot]%prime==(dst.get(key,0)*src[pivot]-dst[pivot]*src.get(key,0))%prime

    shuffled=copy.deepcopy(state);shuffled["actions"].reverse()
    reordered=predictor.predict(shuffled)
    probs2={o["step"]["id"]:o["probability"] for o in reordered["probabilities"]}
    assert max(abs(probs[k]-probs2[k]) for k in probs)<2e-6
    empty=copy.deepcopy(state);empty["actions"]=[]
    assert predictor.predict(empty)["status"]=="no_allowed_action"
    empty["rows"]["target"]=trace["final_master_row"]
    assert predictor.predict(empty)["status"]=="complete"
    write_json(HERE/"runs/example_state.json",state)
    write_json(HERE/"runs/example_prediction.json",prediction)
    size=storage_guard(full=True)
    validation=dict(status="passed",model_hash=result["model_sha256"],seed_model_unchanged=True,
                    checkpoint_matches_final_model=True,training_counts=dict(counts),
                    source_files_verified=len(source_hashes),max_actions=max_actions,
                    saved_features_equal_fresh_encoding=True,trained_candidate_permutation=True,
                    probability_sum_checked=True,selected_exact_update_checked=True,
                    empty_and_complete_states_checked=True,held_out_data_read=False,
                    project_bytes_before_publication=size,model_folder_bytes=folder_size(HERE))
    write_json(HERE/"validation.json",validation)
    first,last=result["history"][0],result["history"][-1]
    # This text documents measurements during training. It makes no test-accuracy claim.
    text=r"""\subsection{Completed training and present scope}
Training used @@STATES@@ recorded states from the 168,330 targets in
693 training families. Of these states, @@CHOICES@@ supplied at least
two allowed actions and @@FORCED@@ supplied one action. The prepared
collection contains @@ACTIONS@@ candidate appearances, with at most
@@MAXACTIONS@@ actions in one state. The model uses 132 features per
candidate and has @@PARAMETERS@@ adjustable parameters.

All selected reference operations reproduced their saved sampled next
rows, and the replay checks verified trace continuity and the final
master support. The audit recorded @@SUPPORTDIFF@@ states in which the
stored symbolic support counts differed from counts in the sampled
matrix. Coefficients can vanish at the chosen kinematic point, so these
states use their exact sampled counts as described above.

The fixed schedule completed ten passes with @@PRESENTATIONS@@
presentations of choice states and @@UPDATES@@ parameter updates.
The mean cross-entropy recorded during parameter updates changed from
@@FIRSTLOSS@@ in the first pass to @@LASTLOSS@@ in the tenth pass.
The corresponding fraction of choices matching the recorded action
changed from @@FIRSTAGREE@@\% to @@LASTAGREE@@\%. These values describe
the training history; the final parameters have not been evaluated
on the reserved families.

Implementation checks verified exact row cancellation, unchanged
predictions when the candidate list or matrix rows are reordered,
invariance of the structural features under nonzero row rescaling,
and the exclusion of future labels from the inputs. The saved model
also reproduced the feature encoding of a recorded training state
and returned probabilities summing to one. A selected operation
passed an independent exact row-update check. The accompanying
implementation retains the trained parameters and the data
provenance~\cite{ReductionModelData}.

These records cover one changing target row with fixed source
identities, predominantly in one-loop families. The model can now
rank the supplied steps at a current state. Tests of full learned
reduction sequences, confidence calibration, unseen families and
integration into Kira remain subsequent stages. In particular, the
present training measurements establish neither a minimum operation
count nor an end-to-end reduction speedup.
"""
    values=dict(STATES=f'{counts["states"]:,}',CHOICES=f'{counts["choice_states"]:,}',
                FORCED=f'{counts["forced_states"]:,}',ACTIONS=f'{counts["candidate_actions"]:,}',
                MAXACTIONS=str(max_actions),PARAMETERS=f'{result["parameter_count"]:,}',
                SUPPORTDIFF=f'{manifest["counts"].get("symbolic_sample_support_count_differences",0):,}',
                PRESENTATIONS=f'{result["choice_state_presentations"]:,}',UPDATES=f'{result["optimizer_updates"]:,}',
                FIRSTLOSS=f'{first["mean_cross_entropy"]:.6g}',LASTLOSS=f'{last["mean_cross_entropy"]:.6g}',
                FIRSTAGREE=f'{100*first["reference_top1"]:.3f}',LASTAGREE=f'{100*last["reference_top1"]:.3f}')
    for key,value in values.items():text=text.replace("@@"+key+"@@",value)
    assert "@@" not in text
    (ROOT/"report/reduction_training.tex").write_text(text,encoding="utf-8")
    write_json(HERE/"runs/report_values.json",values)
    print("Final validation passed",json.dumps(dict(counts)),flush=True)
if __name__=="__main__":main()
