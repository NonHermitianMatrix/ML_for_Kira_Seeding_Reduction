# Shared model calculations

The current production entry point is ../s88_reduce.py. It uses the unchanged seed weights and row weights, unchanged seed thresholds, and unchanged validation-selected routing rule. The older s81_reduce.py interface and its binary remain available.

The seed implementation reuses target-context and target-pair affine prefixes while preserving float32 addition order. All probability vectors are bitwise identical in 36 development contexts. The row implementation evaluates each unordered equation pair once, caches fixed flags, skips zero score coefficients and calculates confidence when a requested record uses it. All six cancellation features match the preceding implementation in 1,000 checks, including invalid expressions and poles.

All 800 implementation-confirmation workflows and 180 validation workflows complete with exact coefficient and decision parity. New/preceding complete-time ratios for seed, row, both and automatic execution are 0.982155, 1.005713, 0.996704, 0.982498. These ratios retain all fallback attempts. Separate comparisons with the new native control appear in confirmation_summary.json; an implementation gain does not itself establish a general ML advantage.

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
