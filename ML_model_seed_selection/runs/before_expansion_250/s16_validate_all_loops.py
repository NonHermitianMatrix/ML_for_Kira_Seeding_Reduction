"""Validate the expanded-data checkpoint and preserve its training provenance."""
import json
import torch
from s01_data import HERE,read,verify_sources
from s12_prepare_features import sha,write
from s02_model import SeedSelector
def main():
 metadata=read(HERE/"trained_model.json");saved=torch.load(HERE/"trained_model.pt",map_location="cpu",weights_only=False)
 latest=torch.load(HERE/"runs/all_loops_latest.pt",map_location="cpu",weights_only=False)
 manifest=read(HERE/"data/manifest.json");split=read(HERE/"split_manifest.json")
 assert metadata["epochs_completed"]==saved["epoch"]==latest["epoch"]==20
 assert len(saved["history"])==len(latest["history"])==20
 assert all(h["targets"]==manifest["training_targets"] for h in saved["history"])
 assert metadata["model_sha256"]==sha(HERE/"trained_model.pt")
 fingerprint=saved["fingerprint"]
 assert fingerprint["config"]==sha(HERE/"config.json") and fingerprint["manifest"]==sha(HERE/"data/manifest.json")
 for name,digest in fingerprint["scripts"].items():assert sha(HERE/name)==digest
 assert verify_sources("train")==saved["manifest_sha256"]==manifest["split_sha256"]
 assert saved["test_targets_processed"]==0 and not metadata["test_data_used"]
 assert latest["partial"]["targets"]==0 and latest["next_family"]==0
 assert latest["lineage"]==metadata["lineage"]==saved["lineage"]
 assert sha(HERE/latest["lineage"]["checkpoint"])==latest["lineage"]["sha256"]
 mixed=read(HERE/"runs/mixed_batch_validation.json")
 assert mixed["status"]=="passed" and not mixed["held_out_data_used"] and mixed["optimizer_updates"]==0
 for name,digest in mixed["source_hashes"].items():assert sha(HERE/name)==digest
 assert all(min(c["term_lengths"])==1 and max(c["term_lengths"])>1 for c in mixed["checks"])
 model=SeedSelector(saved["config"]);model.load_state_dict(saved["model"])
 assert sum(p.numel() for p in model.parameters())==28097
 for k,v in saved["model"].items():
  assert torch.equal(v,latest["model"][k]) and torch.isfinite(v).all()
 assert set(m["loops"] for m in split["families"] if m["split"]=="train")==set(range(1,13))
 result=dict(status="passed",model_sha256=metadata["model_sha256"],expanded_dataset_epochs=20,
  complete_training_target_presentations=20*manifest["training_targets"],optimizer_updates=metadata["optimizer_steps"],
  training_families=manifest["training_families"],training_targets=manifest["training_targets"],
  held_out_families=manifest["held_out_families"],held_out_targets=manifest["held_out_targets"],
  warm_start=latest["lineage"],optimizer_state_preserved=True,compact_weights_equal_resumable_weights=True,
  held_out_data_used=False,current_source_hashes_verified=True,mixed_batch_equivalence=mixed,batch_equivalence=read(HERE/"runs/batch_equivalence.json"))
 write(HERE/"validation.json",result)
 print(json.dumps(result),flush=True)
if __name__=="__main__":main()
