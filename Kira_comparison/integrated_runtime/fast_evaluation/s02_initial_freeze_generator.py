"""Freeze implementation-only changes after exact and timing validation."""
import datetime,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=HERE/"fast_evaluation"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 f=json.loads((EXP/"freeze.json").read_text())
 for n,h in f["sha256"].items():assert sha(ROOT/n)==h,n
 return f
def main():
 assert not (EXP/"freeze.json").exists()
 s=json.loads((EXP/"validation_summary.json").read_text())
 assert s["eligible"] and s["observed"]==s["planned"]==180 and s["all_exact_and_choice_parity"]
 assert json.loads((EXP/"seed_parity.json").read_text())["maximum_probability_difference"]==0
 assert json.loads((EXP/"row_feature_check.json").read_text())["all_passed"]
 paths=[
  "Kira_comparison/integrated_runtime/"+n for n in ["s86_run_shared.py","s87_workflow_shared.py","s88_reduce.py","s89_build_shared.sh","s90_compare_shared.py","s91_validate_shared.sh","s92_summarize_shared.py","s93_freeze_shared.py","s94_confirm_shared.sh","s95_audit_shared.py","s96_finalize_shared.sh","s98_check_shared_application.py","reserved_families.json","deployment.json","s03_records.py"]
 ]+[
  "ML_model_reduction/runtime_training/s15_shared_modular.h","ML_model_reduction/runtime_training/s16_shared_policy.h",
  "ML_model_seed_selection/runtime_inference/s11_shared_runtime.cpp","ML_model_seed_selection/runtime_inference/s12_shared_seed.py",
  "ML_model_seed_selection/runtime_inference/compiled_weights.bin","ML_model_seed_selection/runtime_inference/compiled_export.json",
  "ML_model_seed_selection/runtime_inference/threshold_policy.json",
  ".tools/kira-shared-inference/kira",".tools/kira-shared-inference/libseed.so",
  ".tools/kira-runtime-pair/kira",".tools/kira-seed-inference/libseed.so"
 ]
 paths += [str(p.relative_to(ROOT)) for p in (ROOT/"ML_model_reduction/runtime_training/trajectory_candidates").glob("*/weights.txt")]
 paths += [str(p.relative_to(ROOT)) for p in (HERE/"reserved_references").glob("*.json.gz")]
 for n in ["resource_plan.json","adoption.json","row_feature_check.json","seed_parity.json","validation_summary.json","build.json"]:
  paths.append(str((EXP/n).relative_to(ROOT)))
 f=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repetitions=5,planned=800,methods=["native","seed","row","both","auto"],implementations=["preceding","shared_evaluation"],physical_profiles=8,batches=16,model_weights_thresholds_routing_unchanged=True,scope="Implementation confirmation on the same eight physical profiles used previously; no new independent-family claim.",statistics="Per-batch median of three repeats; geometric mean paired ratios with equal physical-profile weights; descriptive 95% profile bootstrap retaining related batches.",max_concurrent_trials=2,sha256={n:sha(ROOT/n) for n in sorted(set(paths))})
 (EXP/"freeze.json").write_text(json.dumps(f,indent=2)+"\n");verify();print(json.dumps(dict(frozen=True,planned=800)),flush=True)
if __name__=="__main__":main()
