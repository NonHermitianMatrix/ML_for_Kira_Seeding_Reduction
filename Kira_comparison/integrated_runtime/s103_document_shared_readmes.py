"""Update the current integration guide while preserving previous experiment records."""
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=HERE/"fast_evaluation"
def replace_block(path,marker,text):
 old=path.read_text()
 if marker in old:old=old[:old.index(marker)]
 path.write_text(old+"\n"+marker+"\n"+text+"\n")
def main():
 s=json.loads((EXP/"confirmation_summary.json").read_text());audit=json.loads((EXP/"verification.json").read_text());app=json.loads((EXP/"application_verification.json").read_text())
 assert s["observed"]==800 and s["all_exact_and_choice_parity"] and audit["all_passed"] and app["all_passed"]
 comp=s["comparisons"]
 result="All 800 implementation-confirmation workflows and 180 validation workflows complete with exact coefficient and decision parity. New/preceding complete-time ratios for seed, row, both and automatic execution are "+", ".join(f'{comp[m+"_new_over_"+m+"_old"]["complete_seconds"]["all"]["ratio"]:.6f}' for m in ["seed","row","both","auto"])+". These ratios retain all fallback attempts. Separate comparisons with the new native control appear in confirmation_summary.json; an implementation gain does not itself establish a general ML advantage."
 text="""# Shared model calculations

The current production entry point is ../s88_reduce.py. It uses the unchanged seed weights and row weights, unchanged seed thresholds, and unchanged validation-selected routing rule. The older s81_reduce.py interface and its binary remain available.

The seed implementation reuses target-context and target-pair affine prefixes while preserving float32 addition order. All probability vectors are bitwise identical in 36 development contexts. The row implementation evaluates each unordered equation pair once, caches fixed flags, skips zero score coefficients and calculates confidence when a requested record uses it. All six cancellation features match the preceding implementation in 1,000 checks, including invalid expressions and poles.

"""+result+"""

The confirmation reuses eight physical profiles and sixteen batches from the preceding release. It supplies five repeated reductions per method and implementation. It adds no independent families and selects no model weights or thresholds. Native, seed, row, both and automatic modes receive matched input, basis, exact checks and resource settings. Every recorded old/new pair agrees on probability vectors, seed masks, row-choice digests, operations, attempt outcomes and native exports.

Timing begins with workflow preparation and ends after exact reference comparison and cleanup. It includes model loading, feature calculation, prediction, fresh IBP generation, elimination, back substitution and fallback. Reference preparation, interpreter launch, top-level policy lookup and evidence compression remain outside that boundary. Summary intervals resample physical profiles, keeping related batches together. Read all ratios and descriptive intervals before interpreting a gain.

Production use requires a family definition, targets and prescribed master indices. It does not require known target coefficients. Native exact IBP algebra determines the result; exported-basis admission detects incomplete reductions and triggers the fixed fallback. Optional reference mode adds independent coefficient comparisons. Eight shared_application_checks/ runs supply master indices only, then pass independent postrun coefficient checks.

A production call within the bounded scheduled environment is:

    .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s88_reduce.py --family-file CASE.json --masters-file MASTERS.json --size 32 --policy auto --verify-release --output Kira_comparison/integrated_runtime/application_shared/CASE.json.gz

Use one arithmetic worker and node TMPDIR. The scheduled wrapper must permit the native 2400 MiB address-space limit: the current native-check wrapper uses h_data=3G, h_vmem=6G and an outer address-space limit of 2800 MiB. At most two reductions run concurrently, each with 128 MiB scratch. resource_plan.json reserves 9,769,875,456 combined working bytes; this folder shares the parent's 32 MiB retained limit. Tool executables stay under .tools/ and outside Git. Rebuilding produces new binary hashes and needs a new freeze.

The normal sequence is parent s89_build_shared.sh, s91_validate_shared.sh, s97_freeze_shared.sh, s94_confirm_shared.sh and s102_finalize_shared.sh. The last wrapper uses the correct native-process memory allocation for both application checks and the independent audit. The frozen s96_finalize_shared.sh is the earlier 2 GiB wrapper; it can recheck existing application records, but must not launch fresh native application checks. Use s102 for a fresh final audit.

Parent script roles:
- s86_run_shared.py runs one bounded exact native attempt.
- s87_workflow_shared.py executes the fixed fallback and retains all attempts.
- s88_reduce.py exposes native, seed, row, both and automatic execution.
- s89_build_shared.sh builds both optimized components and checks them.
- s90_compare_shared.py rotates old/new complete comparisons.
- s91_validate_shared.sh runs the three validation profiles with at most two workers.
- s92_summarize_shared.py checks parity and computes paired statistics.
- s93_freeze_shared.py fixes all tested code, binaries, models and inputs.
- s94_confirm_shared.sh runs the eight-profile implementation confirmation.
- s95_audit_shared.py independently parses exports and checks rational coefficients and model use.
- s96_finalize_shared.sh preserves the earlier final-check allocation; use s102 for fresh application checks.
- s97_freeze_shared.sh summarizes validation and applies the predefined adoption conditions.
- s98_check_shared_application.py checks basis-only production calls.
- s99_document_shared.py generates the scientific text from completed summaries.
- s100_plot_shared.py draws complete-cost comparisons.
- s101_build_shared_report.sh builds the figure and rendered report.
- s102_finalize_shared.sh performs application checks and final audits with native-compatible memory limits.
- s103_document_shared_readmes.py updates these guides and the release record.
- s104_prepare_shared_report.sh checks completed jobs and resource bounds, publishes checked data, and builds the revised report for review.

Folder checks:
- s00_check_pairs.cpp compares ordered and unordered pair features.
- s01_check_seed.py checks bitwise seed inference and records component costs.
- s02_initial_freeze_generator.py preserves the initial freeze generator as a historical snapshot. Do not execute it here.
- adoption_initial.json preserves the original three-repeat proposal. adoption.json increases confirmation repeats to five before confirmation while retaining the original validation conditions.
- freeze_initial.json preserves the manifest before correcting the textual repetition count. freeze.json records the correction; numeric repetitions, models, methods and inputs were already unchanged.
- shared_validation/ and shared_confirmation/ store complete workflow records. Their attempt records and losslessly shared fields live in the parent folder. Read them with parent s03_records.read_record.
- verification.json and application_verification.json contain the independent checks.
"""
 (EXP/"README.md").write_text(text)
 release=dict(current_entrypoint="Kira_comparison/integrated_runtime/s88_reduce.py",binary=".tools/kira-shared-inference/kira",seed_library=".tools/kira-shared-inference/libseed.so",preceding_entrypoint="Kira_comparison/integrated_runtime/s81_reduce.py",weights_thresholds_routing_unchanged=True,validation_workflows=180,confirmation_workflows=800,basis_only_checks=8,all_exact_checks_passed=True,sha256={})
 for p in [HERE/"s88_reduce.py",HERE/"s102_finalize_shared.sh",EXP/"freeze.json",EXP/"verification.json",EXP/"application_verification.json",EXP/"confirmation_summary.json"]:
  release["sha256"][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 (EXP/"release.json").write_text(json.dumps(release,indent=2)+"\n")
 overview="The current implementation is Kira_comparison/integrated_runtime/s88_reduce.py, described in [the current integration guide](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/main/Kira_comparison/integrated_runtime/fast_evaluation). It reuses seed-network affine prefixes and symmetric row-cancellation calculations while preserving weights and algebraic choices. "+result+" Earlier checkpoints and implementations remain preserved."
 for name in ["README.md","Kira_comparison/README.md","Kira_comparison/integrated_runtime/README.md","ML_model_seed_selection/README.md","ML_model_reduction/README.md"]:
  replace_block(ROOT/name,"<!-- shared-evaluation-current -->",overview)
 replace_block(ROOT/"ML_model_seed_selection/runtime_inference/README.md","<!-- shared-evaluation-current -->","The current backend is s11_shared_runtime.cpp with s12_shared_seed.py and the original compiled_weights.bin. s89_build_shared.sh in the integration folder builds it. Shared affine prefixes preserve the floating-point addition order and give bitwise-identical probabilities in every checked context. The new library stays outside Git; the implementation and unchanged weight export are retained. See fast_evaluation/ for complete timing, exact parity, the freeze and current production entry.")
 replace_block(ROOT/"ML_model_reduction/runtime_training/README.md","<!-- shared-evaluation-current -->","The current runtime headers are s15_shared_modular.h and s16_shared_policy.h. They evaluate each unordered row pair once and reuse its cancellation statistics for both candidate sources. Cached settings, sparse score evaluation and optional confidence calculation reduce repeated work. All six features, source-choice digests and exact results match the preceding implementation in the recorded checks. The selected trajectory weights are unchanged. See Kira_comparison/integrated_runtime/fast_evaluation/ for complete timing, exact checks and the current release.")
 print(json.dumps(dict(readmes_updated=True,release="fast_evaluation/release.json")),flush=True)
if __name__=="__main__":main()
