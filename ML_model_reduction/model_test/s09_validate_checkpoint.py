"""Validate twenty expanded-data passes and freeze the exact checkpoint for testing."""
from s00_test_common import *
import torch
def main():
 metadata=read(MODEL/"trained_model.json");saved=torch.load(MODEL/"trained_model.pt",map_location="cpu",weights_only=False)
 latest=torch.load(MODEL/"runs/all_loops_latest.pt",map_location="cpu",weights_only=False)
 data=read(MODEL/"data/manifest.json")
 split_path=ROOT/"ML_model_seed_selection/split_manifest.json"
 split=read(split_path)["families"];train=[m for m in split if m["split"]=="train"];test=[m for m in split if m["split"]=="test"]
 assert data["split_sha256"]==sha(split_path)
 assert data["train_families"]==len(train) and data["held_out_families"]==len(test)
 assert data["counts"]["targets"]==sum(m["counts"]["targets"] for m in train)
 assert data["held_out_targets"]==sum(m["counts"]["targets"] for m in test)
 assert metadata["counts"]==data["counts"] and metadata["train_families"]==data["train_families"]
 assert metadata["held_out_families"]==data["held_out_families"] and metadata["held_out_targets"]==data["held_out_targets"]
 pilot=read(ROOT/"integrals/expansion_1000/reduction_cpu_thread_pilot.json")
 assert metadata["training_cpu_threads"]==4 and metadata["inference_cpu_threads"]==1
 assert pilot["status"]=="passed" and pilot["optimizer_updates"]==0 and not pilot["held_out_examples_read"]
 assert pilot["warm_checkpoint_sha256"]==metadata["lineage"]["sha256"]
 assert pilot["sources"]["s03_model.py"]==sha(MODEL/"s03_model.py")
 assert metadata["epochs_completed"]==latest["epoch"]==20 and len(latest["history"])==20
 assert all(h["choice_states"]==data["counts"]["choice_states"] for h in latest["history"])
 assert metadata["choice_state_presentations"]==20*data["counts"]["choice_states"]
 assert metadata["model_sha256"]==sha(MODEL/"trained_model.pt")
 assert latest["next_group"]==0 and latest["partial"]["states"]==0
 assert metadata["lineage"]==saved["lineage"]==latest["lineage"]
 assert sha(MODEL/latest["lineage"]["checkpoint"])==latest["lineage"]["sha256"]
 assert not metadata["test_data_used"] and data["held_out_data_read"] is False
 assert saved["fingerprint"]==latest["fingerprint"]==metadata["fingerprint"]
 assert saved["fingerprint"]["manifest_sha256"]==sha(MODEL/"data/manifest.json")
 for key,name in [("config_sha256","config.json"),("model_code_sha256","s03_model.py"),("trainer_sha256","s10_train_all_loops.py")]:
  assert saved["fingerprint"][key]==sha(MODEL/name)
 assert data["preparation_signature"]["encoder_sha256"]==sha(MODEL/"s01_state.py")
 assert data["preparation_signature"]["preparer_sha256"]==sha(MODEL/"s02_prepare_data.py")
 preparation=read(ROOT/"integrals/expansion_1000/parallel_preparation_validation.json")
 assert preparation["status"]=="passed" and preparation["arrays_exactly_equal"]
 assert preparation["preparer_sha256"]==sha(MODEL/"s02_prepare_data.py")
 assert preparation["common_sha256"]==sha(MODEL/"s00_common.py")
 assert preparation["optimizer_updates"]==0 and not preparation["held_out_examples_read"]
 for name,value in saved["model"].items():
  assert torch.equal(value,latest["model"][name]) and torch.isfinite(value).all()
 cfg=read(TEST/"archive_before_all_loops/test_config.json");cfg["model_sha256"]=metadata["model_sha256"]
 cfg["expanded_dataset_epochs"]=20;cfg["parallel_workers"]=4
 write_json(TEST/"test_config.json",cfg)
 result=dict(status="passed",model_sha256=metadata["model_sha256"],expanded_dataset_epochs=20,
   training_families=data["train_families"],held_out_families=data["held_out_families"],
   held_out_targets=data["held_out_targets"],counts=data["counts"],warm_start=metadata["lineage"],
   complete_choice_state_presentations=metadata["choice_state_presentations"],
   compact_weights_equal_resumable_weights=True,current_source_hashes_verified=True,
   test_config_sha256=sha(TEST/"test_config.json"),held_out_data_used=False)
 write_json(TEST/"checkpoint_validation.json",result);write_json(MODEL/"validation.json",result)
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
