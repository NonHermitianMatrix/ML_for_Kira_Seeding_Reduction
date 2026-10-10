"""Freeze exact arithmetic changes before the repeated implementation comparison."""
import datetime,hashlib,json,math,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/parallel_inference"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 f=json.loads((EXP/"freeze.json").read_text())
 for n,h in f["sha256"].items():assert sha(ROOT/n)==h,n
 return f
def main():
 assert not (EXP/"freeze.json").exists()
 v=json.loads((EXP/"validation_summary.json").read_text())
 assert v["observed"]==144 and v["all_exact_and_choice_parity"] and v["eligible"],"Complete-time validation did not meet the predefined conditions"
 a=json.loads((EXP/"arithmetic_check.json").read_text());s=json.loads((EXP/"seed_parity.json").read_text())
 assert a["all_passed"] and a["ratio"]<1 and s["maximum_probability_difference"]==0
 assert math.exp(statistics.mean(math.log(r["new_seconds"]/r["old_seconds"]) for r in s["results"]))<1
 names=["s105_parallel_records.py","s106_run_parallel.py","s107_workflow_parallel.py","s108_reduce.py","s109_build_parallel.sh","s110_compare_parallel.py","s111_validate_parallel.sh","s112_summarize_parallel.py","s113_freeze_parallel.py","s114_confirm_parallel.sh","s115_audit_parallel.py","s116_finalize_parallel.sh","s117_check_parallel_application.py"]
 paths=[HERE/n for n in names]
 paths += [EXP/n for n in ["resource_plan.json","adoption.json","arithmetic_check.json","seed_parity.json","build.json","validation_summary.json","s00_check_arithmetic.cpp","s01_check_seed.py"]]
 paths += [ROOT/".tools/kira-parallel-inference"/n for n in ["kira","libseed.so"]]
 paths += [ROOT/".tools/kira-shared-inference"/n for n in ["kira","libseed.so"]]
 paths += [ROOT/"ML_model_seed_selection/runtime_inference"/n for n in ["s11_shared_runtime.cpp","s12_shared_seed.py","s13_lane_runtime.cpp","s14_lane_seed.py","compiled_weights.bin","compiled_export.json","threshold_policy.json"]]
 paths += [ROOT/"ML_model_reduction/runtime_training"/n for n in ["s06_fast_features.h","s15_shared_modular.h","s16_shared_policy.h","s17_euclid_modular.h","s18_euclid_policy.h"]]
 paths += list((ROOT/"ML_model_reduction/runtime_training/trajectory_candidates").glob("*/weights.txt"))
 paths += [HERE/n for n in ["s00_build.py","s03_records.py","s30_verify.py","s76_summarize_pair_reserved.py","s81_reduce.py","reserved_families.json","families.json","deployment.json"]]
 paths += list((HERE/"reserved_references").glob("*.json.gz"))
 f=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repetitions=5,planned=640,methods=["native","seed","row","both"],implementations=["shared","parallel"],physical_profiles=8,batches=16,model_weights_thresholds_routing_unchanged=True,scope="Same eight physical profiles as previous comparisons; implementation-only confirmation; no new independent-family evidence.",statistics="Per-batch median of five repetitions, equal physical-profile geometric weighting, descriptive 95% profile bootstrap",sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))})
 (EXP/"freeze.json").write_text(json.dumps(f,indent=2)+"\n");verify();print(json.dumps(dict(frozen=True,planned=640)),flush=True)
if __name__=="__main__":main()
