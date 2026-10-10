"""Freeze an unchanged-choice row shortcut only after its validation rule passes."""
import datetime,hashlib,json,pathlib
from s72_summarize_pair import main as summarize
from s49_reserved_references import verify
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 verify();summarize();result=json.loads((HERE/"pair_summary.json").read_text())
 assert not (HERE/"pair_freeze.json").exists()
 if not result["eligible_for_separate_confirmation"]:
  print("Two-row shortcut retained as a development experiment; no confirmation launched.",flush=True);return
 names=[HERE/n for n in ["s68_run_pair.py","s69_workflow_pair.py","s74_reserved_pair.py","s75_reserved_pair.sh","deployment.json","reserved_families.json","pair_protocol.json","cache_resource_plan.json"]]
 names += [ROOT/"ML_model_reduction/runtime_training/s14_pair_policy.h",ROOT/".tools/kira-runtime-pair/kira"]
 names += sorted((HERE/"reserved_references").glob("*.json.gz"))
 frozen=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repetitions=5,variants=["small","fill_small","seed","row","combined"],batches=16,planned=400,parent_freeze_sha256=hashlib.sha256((HERE/"freeze.json").read_bytes()).hexdigest(),
  seed_thresholds="ML_model_seed_selection/runtime_inference/threshold_policy.json",validation="pair_summary.json",
  scope="Implementation confirmation on the same eight previously reserved profiles. No new weights, thresholds or family selection; shared seed settings and row choices remain fixed.",
  statistics="Per-batch medians, equal physical-profile weights, descriptive bootstrap of physical profiles keeping both batches. A secondary within-repeat resampling may assess timing variation.",
  inverse_cache_enabled=False,sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in names})
 (HERE/"pair_freeze.json").write_text(json.dumps(frozen,indent=2)+"\n")
 print(json.dumps(dict(frozen=True,planned=400,unchanged_models=True)),flush=True)
if __name__=="__main__":main()
