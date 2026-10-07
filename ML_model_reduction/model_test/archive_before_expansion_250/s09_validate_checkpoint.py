"""Validate twenty expanded-data passes and freeze the exact checkpoint for testing."""
from s00_test_common import *
import torch
def main():
 metadata=read(MODEL/"trained_model.json");saved=torch.load(MODEL/"trained_model.pt",map_location="cpu",weights_only=False)
 latest=torch.load(MODEL/"runs/all_loops_latest.pt",map_location="cpu",weights_only=False)
 data=read(MODEL/"data/manifest.json")
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
