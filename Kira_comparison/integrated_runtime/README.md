# Integrated native reductions

This extension runs seed selection before native IBP generation and chooses source rows inside Kira's changing symbolic matrix. Earlier models and comparisons remain preserved. The seed checkpoint is unchanged; compiled_weights.bin is an export of its float32 parameters. The separate row policies are selected from complete native training trajectories.

The initial comparison completed all 560 workflows. A 400-workflow implementation confirmation on the same eight physical profiles also completed every target with exact reference agreement. In the confirmation, seed, row and combined complete-time ratios to the smaller native control are 1.154805, 0.998979, 1.159119. The seed ratio for boxes is 0.963700; the aggregate row operation ratio is 0.985327, but its forward-stage time ratio is 1.041202. Neither model has a universal runtime advantage. Read summary.json and pair_reserved_summary.json for grouped intervals, topology results and all failed attempts.

families.json contains six training and three validation physical profiles, each with ordinary and deeper target batches. Related batches share a split. reserved_families.json defines eight new physical profiles and sixteen batches before any reserved timing. freeze.json fixes model files, code, binaries, configuration, thresholds and the five-repeat seven-method protocol. deployment.json records validation-selected settings and automatic method choices. The ladder topology has no new row-training or validation examples.

The models act on exact native IBP reductions over Q(d), with fixed rational kinematics and a prescribed master basis. They neither evaluate master integrals nor provide a generic multiscale or twelve-loop performance claim. Row actions select a source among equations with the same leading integral. The reported operation count is a committed coefficient-update proxy, not Fermat's internal polynomial work.

The common runtime uses bounded dependency-ordered back substitution, compute-node temporary storage and responsive process termination. Both learned and native controls receive these changes. The smaller native control starts at the target bounds and expands if necessary. Learned and deterministic seed subsets fall back to the whole smaller region, then the conservative region. Every attempt contributes to complete time. The native master check is followed by explicit exported-basis admission and exact coefficient comparison. basis_admission_fix.json explains the preserved development rejection; rejected_workflows/ retains its original evidence.

The production workflow includes preparation, model import/loading, prediction, native equation generation, exact reduction, reference comparison, fallback and cleanup. Interpreter launch, common references, shared integrity checks and lossless evidence compression lie outside its time boundary. Methods rotate in order on the same compute node within a profile. Summary intervals resample physical profiles, keeping related batches together.

Use the existing validated Hoffman toolchain and original Kira build under .tools/. s00_build.py applies the row and bounded-back-substitution patch to that build; s44_build_final.sh builds the initial s11_final_policy.h implementation. s67_build_pair.sh builds the current s14_pair_policy.h implementation and records its binary metadata. Seed s06_build_compiled.sh exports unchanged weights, builds the bounded C++ evaluator and checks parity. Tool executables and compiler caches remain outside Git. The final source patch and build metadata are retained here. Rebuilding in another environment creates new binary hashes and requires a new freeze; it does not alter the published frozen evidence.

s81_reduce.py is the integration entry point. Run it in a scheduled job with node TMPDIR, one arithmetic worker, the documented memory limit and an output path inside this experiment folder. Supply one family case JSON object, a batch size and a JSON list of prescribed master indices, or a JSON object with a masters field containing that list. Target reference coefficients are optional. The family object uses the same definition/targets/id/group/topology_group fields as families.json. Select --policy native, seed, row, both, or auto. Auto uses the rule fixed from validation and retains native execution for unknown input classes. The explicit model modes permit controlled transfer tests. It reports the applied policy and complete workflow record. The saved model probabilities express model preference; they are not calibrated guarantees.

A typical command in that bounded scheduled environment is:

    .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s81_reduce.py --family-file CASE.json --size 32 --masters-file MASTERS.json --output Kira_comparison/integrated_runtime/application/CASE.json.gz --policy auto

The interface calculates target coefficients from native exact IBP identities and row operations. It admits a result only when every target is reduced and each right-hand-side integral belongs to the prescribed basis; otherwise it expands the seed region. An optional --reference RECORD.json.gz replaces --masters-file and adds an independent coefficient comparison. The records distinguish native_exact_basis from reference_coefficients. Eight application checks provide only master indices to the reducer, then pass independent postrun coefficient comparisons. application_verification.json records these checks and source hashes. Basis discovery is separate preparation. Complete trials reuse no previous equation database. The application record includes input/routing and workflow time; evidence compression and optional release hash checks remain outside this boundary.

resource_plan.json and cache_resource_plan.json reserve at most 9,753,098,240 combined bytes, less than 10,000,000,000 combined project bytes, including local report copies, publication objects, caches and scratch. At most two production reductions use 128 MiB scratch each, or one reference uses 256 MiB. Solver address space is 2400 MiB and monitored solver-tree RSS is bounded at 2100 MiB. The retained cap covers this folder and both new model-runtime folders. Atomic shared records enforce that cap. Do not launch reference and production arrays together.

pair_freeze.json freezes the two-row implementation and the 400-workflow confirmation. pair_reserved_test/ repeats the original eight reserved profiles with five methods and five repetitions per batch; it adds no independent physical families. pair_summary.json records 144 validation workflows with unchanged decisions and exact outputs. cache_summary.json retains the rejected inverse-cache experiment. s79_run_application.py and s80_workflow_application.py implement optional-reference production use; s81_reduce.py is the current public entry point. application_checks/ retains the eight basis-only interface checks.

shared/ stores content-addressed compressed fields; workflow_attempts/ retains every attempt. Use s03_records.read_record to restore a record. Validation folders preserve earlier alternatives, including rejected database settings and failed scheduling pilots. These results are not removed when a faster configuration is selected. s30_verify.py checks shared hashes, reparses exports independently, compares exact rational polynomials and audits workflow accounting.

The normal sequence is development/collection, fitting, parity checks, validation, freeze, sequential references, reserved tests, summary/audit, plots and report. s55_freeze_and_references.sh combines freeze and references for a fresh experiment. Existing frozen files and records are immutable; use a distinct experiment for another tuning cycle. s47_basis_admission.py is the retained one-time development migration and must not be reapplied to finished data.

## Script order

- s00_build.py: Patch source selection inside native Kira and reuse the responsive shutdown.
- s01_build.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py
- s02_run.py: Run one bounded complete Kira reduction, retaining compact exact evidence.
- s03_records.py: Losslessly share scientific evidence with atomic writes and a storage bound.
- s04_pilot.py: Check exact bounded back substitution and unchanged learned policies.
- s05_pilot.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s04_pilot.py
- s06_build_modular.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s04_test_features.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py
- s07_collect.py: Collect exact local symbolic costs across ordinary and deeper target batches.
- s08_collect.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s07_collect.py
- s09_train.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s05_train.py
- s10_verify_seed.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s01_verify.py
- s11_scratch_pilot.py: Measure project and node scratch with exact, matched native reductions.
- s12_scratch_pilot.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s11_scratch_pilot.py
- s13_ordering_probe.py: Compare the eight supported integral orderings on validation cases.
- s14_runtime_config.py: Choose temporary-storage placement from the separate exact native pilot.
- s15_ordering_probe.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s13_ordering_probe.py
- s16_validate_rows.py: Test repeated row decisions in fresh native reductions on validation cases.
- s17_validate_rows.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s16_validate_rows.py
- s18_build_fast_rows.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py
- s19_verify_fast_rows.py: Verify shared feature formulas and native tree scores in exact reductions.
- s20_verify_fast_rows.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s19_verify_fast_rows.py
- s21_trajectory_search.py: Measure complete native trajectories for a bounded learned cost-policy search.
- s22_trajectory_search.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s21_trajectory_search.py
- s23_validate_trajectories.py: Measure learned trajectory policies and seed integration on development validation.
- s24_workflow.py: Run a complete fixed fallback policy; all production costs are retained.
- s25_select_trajectory.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s09_select_trajectory.py
- s26_validate_trajectories.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s23_validate_trajectories.py
- s27_build_ephemeral_db.py: Build opt-in database settings restricted to disposable trial directories.
- s28_build_ephemeral_db.sh: Scheduler/build wrapper: python3 Kira_comparison/integrated_runtime/s27_build_ephemeral_db.py
- s29_ephemeral_pilot.py: Counterbalanced exact comparison of disposable database settings.
- s30_verify.py: Independently check all retained exact exports and complete workflow accounting.
- s31_development_summary.py: Summarize complete trajectory validation without using reserved measurements.
- s32_test_database_guard.py: Verify disposable-directory guards against actual compiled database helper.
- s33_test_database_guard.sh: Scheduler/build wrapper: python3 Kira_comparison/integrated_runtime/s32_test_database_guard.py
- s34_reserved_families.py: Define fresh physical test profiles before inspecting any reserved reductions.
- s35_profile_preparation.py: Profile preparation on one validation case without using the timing as a benchmark.
- s36_build_sparse_rows.py: Specialize feature construction for the fitted sparse linear row policies.
- s37_build_sparse_rows.sh: Scheduler/build wrapper: python3 Kira_comparison/integrated_runtime/s36_build_sparse_rows.py; KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-sparse KIRA_RUNTIME_HEADER=s10_sparse_policy.h KIRA_COST_BUILD_RECORD=sparse_rows_build.json KIRA_COST_PATCH=reduction_sparse_rows.patch python3 Kira_comparison/integrated_runtime/s00_build.py
- s38_validate_sparse_rows.py: Verify sparse feature decisions and measure the selected policies with shared controls.
- s39_validate_sparse_rows.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s38_validate_sparse_rows.py
- s40_seed_threshold_search.py: Fit seed thresholds from complete training workflows, retaining failed attempts.
- s41_seed_threshold_search.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s40_seed_threshold_search.py
- s42_fit_seed_thresholds.sh: Scheduler/build wrapper: python3 ML_model_seed_selection/runtime_inference/s10_fit_thresholds.py
- s43_finalize_controls.py: Apply model-free controls and the same needed-feature optimization to all row policies.
- s44_build_final.sh: Scheduler/build wrapper: python3 Kira_comparison/integrated_runtime/s43_finalize_controls.py; KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-final KIRA_RUNTIME_HEADER=s11_final_policy.h KIRA_COST_BUILD_RECORD=final_rows_build.json KIRA_COST_PATCH=reduction_final_rows.patch python3 Kira_comparison/integrated_runtime/s00_build.py
- s45_validate_integrated.py: Validate fitted thresholds and row policies against the smaller native control.
- s46_validate_integrated.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s45_validate_integrated.py
- s47_basis_admission.py: Reject exports with unresolved integrals before coefficient comparison.
- s48_freeze_integrated.py: Select on validation and freeze before any new reserved reduction.
- s49_reserved_references.py: Prepare common native master bases sequentially under the reference budget.
- s50_reserved_references.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s49_reserved_references.py
- s51_reserved_test.py: Run frozen, counterbalanced full-workflow ablations on new physical profiles.
- s52_reserved_test.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s51_reserved_test.py
- s53_summarize_reserved.py: Summarize every frozen trial, preserving failures and grouped paired timing.
- s54_plot_reserved.py: Render exact paired complete-time and operation comparisons.
- s55_freeze_and_references.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s48_freeze_integrated.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s49_reserved_references.py
- s56_reduce.py: Apply the frozen integrated policy to a complete physical-family batch.
- s57_document.py: Write the scientific report from frozen exact-test summaries.
- s58_build_report.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s54_plot_reserved.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s85_plot_pair.py
- s59_audit.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s53_summarize_reserved.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s66_summarize_cache.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s30_verify.py
- s60_document_readmes.py: Maintain the integration and model guides from the retained run state.
- s61_run_cached.py: Run one bounded complete Kira reduction, retaining compact exact evidence.
- s62_workflow_cached.py: Run a complete fixed fallback policy; all production costs are retained.
- s63_build_cached.sh: Scheduler/build wrapper: KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-cached KIRA_RUNTIME_HEADER=s13_cached_policy.h KIRA_COST_BUILD_RECORD=cached_build.json KIRA_COST_PATCH=reduction_cached.patch python3 Kira_comparison/integrated_runtime/s00_build.py
- s64_validate_cache.py: Check inverse-cache parity and full workflow cost on validation profiles only.
- s65_validate_cache.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s64_validate_cache.py
- s66_summarize_cache.py: Assess a numerically identical inverse cache using validation only.
- s67_build_pair.sh: Scheduler/build wrapper: KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-pair KIRA_RUNTIME_HEADER=s14_pair_policy.h KIRA_COST_BUILD_RECORD=pair_build.json KIRA_COST_PATCH=reduction_pair.patch python3 Kira_comparison/integrated_runtime/s00_build.py
- s68_run_pair.py: Run one bounded complete Kira reduction, retaining compact exact evidence.
- s69_workflow_pair.py: Run a complete fixed fallback policy; all production costs are retained.
- s70_validate_pair.py: Check two-row shortcut parity and full workflow cost on validation profiles only.
- s71_validate_pair.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s70_validate_pair.py
- s72_summarize_pair.py: Assess a numerically identical two-row shortcut using validation only.
- s73_freeze_pair.py: Freeze an unchanged-choice row shortcut only after its validation rule passes.
- s74_reserved_pair.py: Run frozen, counterbalanced full-workflow ablations on new physical profiles.
- s75_reserved_pair.sh: Scheduler/build wrapper:  .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s74_reserved_pair.py
- s76_summarize_pair_reserved.py: Summarize every frozen trial, preserving failures and grouped paired timing.
- s77_audit_final.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s53_summarize_reserved.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s66_summarize_cache.py;  .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s72_summarize_pair.py;  .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s76_summarize_pair_reserved.py; .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s30_verify.py
- s78_freeze_pair.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s73_freeze_pair.py
- s79_run_application.py: Run one bounded complete Kira reduction, retaining compact exact evidence.
- s80_workflow_application.py: Run a complete fixed fallback policy; all production costs are retained.
- s81_reduce.py: Reduce new targets with a known master basis; reference answers are optional.
- s82_check_application.py: Check real basis-only reductions against reference answers after execution.
- s83_check_application.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s82_check_application.py
- s84_document_pair.py: Document the unchanged-choice shortcut and the usable basis-only interface.
- s85_plot_pair.py: Plot complete and forward-stage costs after the two-row shortcut.

<!-- shared-evaluation-current -->
The preceding implementation is Kira_comparison/integrated_runtime/s88_reduce.py, described in [the current integration guide](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/main/Kira_comparison/integrated_runtime/fast_evaluation). It reuses seed-network affine prefixes and symmetric row-cancellation calculations while preserving weights and algebraic choices. All 800 implementation-confirmation workflows and 180 validation workflows complete with exact coefficient and decision parity. New/preceding complete-time ratios for seed, row, both and automatic execution are 0.982155, 1.005713, 0.996704, 0.982498. These ratios retain all fallback attempts. Separate comparisons with the new native control appear in confirmation_summary.json; an implementation gain does not itself establish a general ML advantage. Earlier checkpoints and implementations remain preserved.

<!-- parallel-inference-current -->
The latest production entry is Kira_comparison/integrated_runtime/s108_reduce.py. [The current guide](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/main/Kira_comparison/parallel_inference) describes parallel neural outputs, exact modular inverses and reduced row-feature allocation. All 144 final-candidate validation workflows and 640 confirmation workflows preserve exact coefficients, seed probabilities, source-row digests and committed operation counts. The complete-time new/preceding ratios for seed, row and combined execution are 0.989778, 0.989961, 0.984075. All fallback costs are included. All three complete-time intervals include one, so the component gain is clearer than the full-workflow change. Seed and combined aggregate costs remain above the native control; the row-only interval against native also includes one. See confirmation_summary.json for descriptive intervals and topology results. The rejected development candidate and all preceding releases remain preserved.
