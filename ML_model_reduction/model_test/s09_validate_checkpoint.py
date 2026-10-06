"""Check the current continued checkpoint without training or changing test outputs."""
import copy,json,sys
import numpy as np
import torch
from s00_test_common import ROOT,MODEL,TEST,read,sha,write_json
from s01_state import column,eliminate
from s05_predict import Predictor

def main():
    torch.set_num_threads(1)
    metadata=read(MODEL/"trained_model.json")
    request=read(TEST/"evaluation_request.json")
    continuation=read(MODEL/"runs/extra_20_epochs/request.json")
    model=torch.load(MODEL/"trained_model.pt",map_location="cpu",weights_only=False)
    latest=torch.load(MODEL/"runs/latest.pt",map_location="cpu",weights_only=False)
    assert metadata["epochs_completed"]==request["epochs_completed"]==latest["epoch"]==30
    assert latest["next_group"]==0 and latest["history"]==metadata["history"]
    assert len(latest["history"])==30
    assert sum(x["updates"] for x in latest["history"])==metadata["optimizer_updates"]
    assert metadata["choice_state_presentations"]==30*metadata["counts"]["choice_states"]
    assert metadata["model_sha256"]==request["model_sha256"]==sha(MODEL/"trained_model.pt")
    assert all(torch.equal(v,latest["model"][k]) and torch.isfinite(v).all() for k,v in model["model"].items())
    fingerprints=metadata["fingerprint"]
    paths={"config_sha256":"config.json","manifest_sha256":"data/manifest.json",
           "model_code_sha256":"s03_model.py","trainer_sha256":"s04_train.py",
           "continuation_trainer_sha256":"runs/extra_20_epochs/s00_continue.py",
           "request_sha256":"runs/extra_20_epochs/request.json"}
    for key,path in paths.items():assert fingerprints[key]==sha(MODEL/path),(key,path)
    manifest=read(MODEL/"data/manifest.json")
    assert manifest["split_sha256"]==sha(ROOT/"ML_model_seed_selection/split_manifest.json")
    assert manifest["preparation_signature"]["encoder_sha256"]==sha(MODEL/"s01_state.py")
    assert read(MODEL/"implementation_checks.json")["status"]=="passed"
    state=read(MODEL/"runs/example_state.json")
    before=sha(MODEL/"trained_model.pt")
    predictor=Predictor();prediction=predictor.predict(state,apply=True)
    probs={o["step"]["id"]:o["probability"] for o in prediction["probabilities"]}
    assert abs(sum(probs.values())-1)<1e-6
    assert prediction["confidence"]==max(probs.values())
    selected=prediction["selected_step"];src=state["rows"][selected["source_row"]];dst=state["rows"][selected["destination_row"]]
    pivot=column(selected["pivot_indices"]);prime=state["prime"]
    after=prediction["exact_update"]["coefficients"]
    for key in set(src)|set(dst)|set(after):
        assert after.get(key,0)*src[pivot]%prime==(dst.get(key,0)*src[pivot]-dst[pivot]*src.get(key,0))%prime
    shuffled=copy.deepcopy(state);shuffled["actions"].reverse()
    reordered=predictor.predict(shuffled)
    probs2={o["step"]["id"]:o["probability"] for o in reordered["probabilities"]}
    assert max(abs(probs[k]-probs2[k]) for k in probs)<2e-6
    assert sha(MODEL/"trained_model.pt")==before
    write_json(MODEL/"runs/example_prediction.json",prediction)
    values=read(MODEL/"runs/report_values.json")
    last=metadata["history"][-1]
    values.update(EPOCHS="30",PRESENTATIONS=format(metadata["choice_state_presentations"],","),
                  UPDATES=format(metadata["optimizer_updates"],","),
                  LASTLOSS=format(last["mean_cross_entropy"],".6g"),
                  LASTAGREE=format(100*last["reference_top1"],".3f"))
    write_json(MODEL/"runs/report_values.json",values)
    record=dict(status="passed",model_hash=before,epochs_completed=30,
        checkpoint_matches_final_model=True,history_and_update_counts_checked=True,
        training_source_fingerprints_verified=True,training_counts=metadata["counts"],
        split_and_encoder_unchanged=True,probability_sum_checked=True,
        trained_candidate_permutation=True,selected_exact_update_checked=True,
        weights_unchanged=True,optimizer_updates_during_check=0,
        scope="Current frozen checkpoint and training-state interface checks; complete held-out replay is in model_test/validation.json.")
    write_json(TEST/"checkpoint_validation.json",record)
    write_json(MODEL/"validation.json",record)
    print("Thirty-epoch checkpoint checks passed",flush=True)

if __name__=="__main__":main()
