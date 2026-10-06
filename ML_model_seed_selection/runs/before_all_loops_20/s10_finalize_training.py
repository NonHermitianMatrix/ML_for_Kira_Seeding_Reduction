"""Verify the saved training artifact and update status documentation; never run testing."""
import hashlib,json,math,subprocess
from pathlib import Path
import torch
from s01_data import HERE,ROOT,read
torch.set_num_threads(1)
status=read(HERE/"runs"/"training_status.json")
model_path=HERE/"trained_model.pt"
saved=torch.load(str(model_path),map_location="cpu")
cfg=saved["config"]
assert status["status"]==saved["status"]=="trained"
assert saved["epoch"]==status["completed_epochs"]==cfg["epochs"]==10
assert saved["trained_targets"]==168330*10
assert saved["optimizer_steps"]==math.ceil(168330/cfg["accumulate_targets"])*10
assert saved["test_targets_processed"]==0 and not status["testing_performed"]
assert len(saved["history"])==10 and all(r["targets"]==168330 for r in saved["history"])
assert all(torch.isfinite(t).all() for t in saved["model"].values())
assert sum(t.numel() for t in saved["model"].values())==28097
digest=hashlib.sha256(model_path.read_bytes()).hexdigest()
result=dict(status="trained_testing_deferred",epochs=10,training_targets_per_epoch=168330,
            training_families=693,optimizer_steps=saved["optimizer_steps"],
            target_presentations=saved["trained_targets"],parameters=28097,
            final_training_loss=saved["history"][-1]["mean_loss"],
            training_elapsed_seconds=saved["elapsed_seconds"],
            model_file="trained_model.pt",model_sha256=digest,model_bytes=model_path.stat().st_size,
            resume_checkpoint="runs/latest.pt",test_targets_processed=0,testing_performed=False,
            source_commit=saved["source_commit"],source_files=saved["source_files"],
            manifest_sha256=saved["manifest_sha256"])
(HERE/"trained_model.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
(HERE/"runs"/"README.md").write_text(
    "# Seed-model training run\n\nTraining completed all ten passes through 168,330 training targets. "+
    "The run made "+str(saved["optimizer_steps"])+" optimizer updates. "+
    "No held-out model testing was performed.\n\n"+
    "../trained_model.pt contains the final model, and latest.pt also retains optimizer state. "+
    "training.jsonl records each completed epoch. training_status.json gives the final status, "+
    "input_checks.json records the training-only input checks, and scheduler.log contains the job output. "+
    "The model fingerprint and training source provenance are in ../trained_model.json.\n",
    encoding="utf-8")
paragraph=("<!-- training-status:start -->\n"
           "Training completed ten epochs on 168,330 training targets from 693 families. "
           "The final model is [trained_model.pt](trained_model.pt), with metadata in "
           "[trained_model.json](trained_model.json). The resume checkpoint and training history are in "
           "[runs](runs/README.md). No test examples were used in training or evaluated. Testing awaits the user's instruction.\n"
           "<!-- training-status:end -->")
p=HERE/"README.md";text=p.read_text(encoding="utf-8")
start=text.index("<!-- training-status:start -->")
end=text.index("<!-- training-status:end -->",start)+len("<!-- training-status:end -->")
p.write_text(text[:start]+paragraph+text[end:],encoding="utf-8")
p=ROOT/"README.md";text=p.read_text(encoding="utf-8")
start=text.index("<!-- seed-training-status:start -->")
end=text.index("<!-- seed-training-status:end -->",start)+len("<!-- seed-training-status:end -->")
para=("<!-- seed-training-status:start -->\n"
      "The seed-selection model completed ten training epochs. Its [trained weights](ML_model_seed_selection/trained_model.pt) "
      "and [training metadata](ML_model_seed_selection/trained_model.json) are stored in the model folder. "
      "The held-out test set remains unused for model evaluation.\n<!-- seed-training-status:end -->")
p.write_text(text[:start]+para+text[end:],encoding="utf-8")
print(json.dumps(result),flush=True)
