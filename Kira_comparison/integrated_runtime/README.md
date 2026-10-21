# Native integration and complete reduction cost

This directory tests changes inside Kira and in the application that calls it. The experiments measure seed and row decisions, equation preparation, temporary storage, shared evaluation, and prediction overhead. Each comparison records its own controls and exact checks.

Inputs are physical families, target batches, prescribed bases, and the settings fixed by the named study. Outputs include coefficients, operation records, timing summaries, and failed attempts. Subfolders separate pilots, validation, reserved tests, and application checks. The script table identifies the producer for each part; use its scheduler wrapper and preserve its frozen inputs.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Scripts

| File | Purpose |
|---|---|
| [ephemeral_database.patch](ephemeral_database.patch) | This patch records changes to the native Kira source. |
| [reduction_cached.patch](reduction_cached.patch) | This patch records changes to the native Kira source. |
| [reduction_cost.patch](reduction_cost.patch) | This patch records changes to the native Kira source. |
| [reduction_fast_rows.patch](reduction_fast_rows.patch) | This patch records changes to the native Kira source. |
| [reduction_final_rows.patch](reduction_final_rows.patch) | This patch records changes to the native Kira source. |
| [reduction_modular.patch](reduction_modular.patch) | This patch records changes to the native Kira source. |
| [reduction_pair.patch](reduction_pair.patch) | This patch records changes to the native Kira source. |
| [reduction_sparse_rows.patch](reduction_sparse_rows.patch) | This patch records changes to the native Kira source. |
| [s00_build.py](s00_build.py) | Patches source selection inside native Kira and reuse the responsive shutdown. |
| [s01_build.sh](s01_build.sh) | Scheduler wrapper for build; its header sets the resource limits. |
| [s02_run.py](s02_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s03_records.py](s03_records.py) | Shares scientific evidence with atomic writes and a storage bound. |
| [s04_pilot.py](s04_pilot.py) | Check exact bounded back substitution and unchanged learned policies. |
| [s05_pilot.sh](s05_pilot.sh) | Scheduler wrapper for pilot; its header sets the resource limits. |
| [s06_build_modular.sh](s06_build_modular.sh) | Scheduler wrapper for build modular; its header sets the resource limits. |
| [s07_collect.py](s07_collect.py) | Collect exact local symbolic costs across ordinary and deeper target batches. |
| [s08_collect.sh](s08_collect.sh) | Scheduler wrapper for collect; its header sets the resource limits. |
| [s09_train.sh](s09_train.sh) | Scheduler wrapper for train; its header sets the resource limits. |
| [s100_plot_shared.py](s100_plot_shared.py) | Plot complete times relative to the preceding implementation and native control. |
| [s101_build_shared_report.sh](s101_build_shared_report.sh) | Scheduler wrapper for build shared report; its header sets the resource limits. |
| [s102_finalize_shared.sh](s102_finalize_shared.sh) | Scheduler wrapper for finalize shared; its header sets the resource limits. |
| [s103_document_shared_readmes.py](s103_document_shared_readmes.py) | Updates the current integration guide while preserving previous experiment records. |
| [s104_prepare_shared_report.sh](s104_prepare_shared_report.sh) | Scheduler wrapper for prepare shared report; its header sets the resource limits. |
| [s105_parallel_records.py](s105_parallel_records.py) | Bounds new evidence separately and reuse unchanged immutable field blobs. |
| [s106_run_parallel.py](s106_run_parallel.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s107_workflow_parallel.py](s107_workflow_parallel.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s108_reduce.py](s108_reduce.py) | Reduces new targets with a known master basis; reference answers are optional. |
| [s109_build_parallel.sh](s109_build_parallel.sh) | Scheduler wrapper for build parallel; its header sets the resource limits. |
| [s10_verify_seed.sh](s10_verify_seed.sh) | Scheduler wrapper for verify seed; its header sets the resource limits. |
| [s110_compare_parallel.py](s110_compare_parallel.py) | Compare old and shared inference with fixed weights and exact native reductions. |
| [s111_validate_parallel.sh](s111_validate_parallel.sh) | Scheduler wrapper for validate parallel; its header sets the resource limits. |
| [s112_summarize_parallel.py](s112_summarize_parallel.py) | Retains all matched complete costs and independently assert unchanged decisions. |
| [s113_freeze_parallel.py](s113_freeze_parallel.py) | Freeze exact arithmetic changes before the repeated implementation comparison. |
| [s114_confirm_parallel.sh](s114_confirm_parallel.sh) | Scheduler wrapper for confirm parallel; its header sets the resource limits. |
| [s115_audit_parallel.py](s115_audit_parallel.py) | Check new exact coefficients, timing accounting and native model use. |
| [s116_finalize_parallel.sh](s116_finalize_parallel.sh) | Scheduler wrapper for finalize parallel; its header sets the resource limits. |
| [s117_check_parallel_application.py](s117_check_parallel_application.py) | Check real basis-only reductions against reference answers after execution. |
| [s118_freeze_parallel.sh](s118_freeze_parallel.sh) | Scheduler wrapper for freeze parallel; its header sets the resource limits. |
| [s119_document_parallel.py](s119_document_parallel.py) | Write the mathematical changes and measured complete costs from verified data. |
| [s11_scratch_pilot.py](s11_scratch_pilot.py) | Measures project and node scratch with exact, matched native reductions. |
| [s120_plot_parallel.py](s120_plot_parallel.py) | Plot complete times relative to the preceding implementation and native control. |
| [s121_build_parallel_report.sh](s121_build_parallel_report.sh) | Scheduler wrapper for build parallel report; its header sets the resource limits. |
| [s122_document_parallel_readmes.py](s122_document_parallel_readmes.py) | Document the current exact implementation and the rejected development candidate. |
| [s123_prepare_parallel_report.sh](s123_prepare_parallel_report.sh) | Scheduler wrapper for prepare parallel report; its header sets the resource limits. |
| [s12_scratch_pilot.sh](s12_scratch_pilot.sh) | Scheduler wrapper for scratch pilot; its header sets the resource limits. |
| [s13_ordering_probe.py](s13_ordering_probe.py) | Compare the eight supported integral orderings on validation cases. |
| [s14_runtime_config.py](s14_runtime_config.py) | Chooses temporary-storage placement from the separate exact native pilot. |
| [s15_ordering_probe.sh](s15_ordering_probe.sh) | Scheduler wrapper for ordering probe; its header sets the resource limits. |
| [s16_validate_rows.py](s16_validate_rows.py) | Test repeated row decisions in fresh native reductions on validation cases. |
| [s17_validate_rows.sh](s17_validate_rows.sh) | Scheduler wrapper for validate rows; its header sets the resource limits. |
| [s18_build_fast_rows.sh](s18_build_fast_rows.sh) | Scheduler wrapper for build fast rows; its header sets the resource limits. |
| [s19_verify_fast_rows.py](s19_verify_fast_rows.py) | Verify shared feature formulas and native tree scores in exact reductions. |
| [s20_verify_fast_rows.sh](s20_verify_fast_rows.sh) | Scheduler wrapper for verify fast rows; its header sets the resource limits. |
| [s21_trajectory_search.py](s21_trajectory_search.py) | Measures complete native trajectories for a bounded learned cost-policy search. |
| [s22_trajectory_search.sh](s22_trajectory_search.sh) | Scheduler wrapper for trajectory search; its header sets the resource limits. |
| [s23_validate_trajectories.py](s23_validate_trajectories.py) | Measures learned trajectory policies and seed integration on development validation. |
| [s24_workflow.py](s24_workflow.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s25_select_trajectory.sh](s25_select_trajectory.sh) | Scheduler wrapper for select trajectory; its header sets the resource limits. |
| [s26_validate_trajectories.sh](s26_validate_trajectories.sh) | Scheduler wrapper for validate trajectories; its header sets the resource limits. |
| [s27_build_ephemeral_db.py](s27_build_ephemeral_db.py) | Build opt-in database settings restricted to disposable trial directories. |
| [s28_build_ephemeral_db.sh](s28_build_ephemeral_db.sh) | Scheduler wrapper for build ephemeral db; its header sets the resource limits. |
| [s29_ephemeral_pilot.py](s29_ephemeral_pilot.py) | Counterbalanced exact comparison of disposable database settings. |
| [s30_verify.py](s30_verify.py) | Check all retained exact exports and complete workflow accounting. |
| [s31_development_summary.py](s31_development_summary.py) | Summarize complete trajectory validation without using reserved measurements. |
| [s32_test_database_guard.py](s32_test_database_guard.py) | Verify disposable-directory guards against actual compiled database helper. |
| [s33_test_database_guard.sh](s33_test_database_guard.sh) | Scheduler wrapper for test database guard; its header sets the resource limits. |
| [s34_reserved_families.py](s34_reserved_families.py) | Defines fresh physical test profiles before inspecting any reserved reductions. |
| [s35_profile_preparation.py](s35_profile_preparation.py) | Profiles preparation on one validation case without using the timing as a benchmark. |
| [s36_build_sparse_rows.py](s36_build_sparse_rows.py) | Specializes feature construction for the fitted sparse linear row policies. |
| [s37_build_sparse_rows.sh](s37_build_sparse_rows.sh) | Scheduler wrapper for build sparse rows; its header sets the resource limits. |
| [s38_validate_sparse_rows.py](s38_validate_sparse_rows.py) | Verify sparse feature decisions and measure the selected policies with shared controls. |
| [s39_validate_sparse_rows.sh](s39_validate_sparse_rows.sh) | Scheduler wrapper for validate sparse rows; its header sets the resource limits. |
| [s40_seed_threshold_search.py](s40_seed_threshold_search.py) | Fit seed thresholds from complete training workflows, retaining failed attempts. |
| [s41_seed_threshold_search.sh](s41_seed_threshold_search.sh) | Scheduler wrapper for seed threshold search; its header sets the resource limits. |
| [s42_fit_seed_thresholds.sh](s42_fit_seed_thresholds.sh) | Scheduler wrapper for fit seed thresholds; its header sets the resource limits. |
| [s43_finalize_controls.py](s43_finalize_controls.py) | Applies model-free controls and the same needed-feature optimization to all row policies. |
| [s44_build_final.sh](s44_build_final.sh) | Scheduler wrapper for build final; its header sets the resource limits. |
| [s45_validate_integrated.py](s45_validate_integrated.py) | Validates fitted thresholds and row policies against the smaller native control. |
| [s46_validate_integrated.sh](s46_validate_integrated.sh) | Scheduler wrapper for validate integrated; its header sets the resource limits. |
| [s47_basis_admission.py](s47_basis_admission.py) | Rejects exports with unresolved integrals before coefficient comparison. |
| [s48_freeze_integrated.py](s48_freeze_integrated.py) | Select on validation and freeze before any new reserved reduction. |
| [s49_reserved_references.py](s49_reserved_references.py) | Prepare common native master bases sequentially under the reference budget. |
| [s50_reserved_references.sh](s50_reserved_references.sh) | Scheduler wrapper for reserved references; its header sets the resource limits. |
| [s51_reserved_test.py](s51_reserved_test.py) | Run frozen, counterbalanced full-workflow ablations on new physical profiles. |
| [s52_reserved_test.sh](s52_reserved_test.sh) | Scheduler wrapper for reserved test; its header sets the resource limits. |
| [s53_summarize_reserved.py](s53_summarize_reserved.py) | Summarize every frozen trial, preserving failures and grouped paired timing. |
| [s54_plot_reserved.py](s54_plot_reserved.py) | Renders exact paired complete-time and operation comparisons. |
| [s55_freeze_and_references.sh](s55_freeze_and_references.sh) | Scheduler wrapper for freeze and references; its header sets the resource limits. |
| [s56_reduce.py](s56_reduce.py) | Applies the frozen integrated policy to a complete physical-family batch. |
| [s57_document.py](s57_document.py) | Write the scientific report from frozen exact-test summaries. |
| [s58_build_report.sh](s58_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |
| [s59_audit.sh](s59_audit.sh) | Scheduler wrapper for audit; its header sets the resource limits. |
| [s60_document_readmes.py](s60_document_readmes.py) | Maintains the integration and model guides from the retained run state. |
| [s61_run_cached.py](s61_run_cached.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s62_workflow_cached.py](s62_workflow_cached.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s63_build_cached.sh](s63_build_cached.sh) | Scheduler wrapper for build cached; its header sets the resource limits. |
| [s64_validate_cache.py](s64_validate_cache.py) | Check inverse-cache parity and full workflow cost on validation profiles only. |
| [s65_validate_cache.sh](s65_validate_cache.sh) | Scheduler wrapper for validate cache; its header sets the resource limits. |
| [s66_summarize_cache.py](s66_summarize_cache.py) | Assesss a numerically identical inverse cache using validation only. |
| [s67_build_pair.sh](s67_build_pair.sh) | Scheduler wrapper for build pair; its header sets the resource limits. |
| [s68_run_pair.py](s68_run_pair.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s69_workflow_pair.py](s69_workflow_pair.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s70_validate_pair.py](s70_validate_pair.py) | Check two-row shortcut parity and full workflow cost on validation profiles only. |
| [s71_validate_pair.sh](s71_validate_pair.sh) | Scheduler wrapper for validate pair; its header sets the resource limits. |
| [s72_summarize_pair.py](s72_summarize_pair.py) | Assesss a numerically identical two-row shortcut using validation only. |
| [s73_freeze_pair.py](s73_freeze_pair.py) | Freeze an unchanged-choice row shortcut only after its validation rule passes. |
| [s74_reserved_pair.py](s74_reserved_pair.py) | Run frozen, counterbalanced full-workflow ablations on new physical profiles. |
| [s75_reserved_pair.sh](s75_reserved_pair.sh) | Scheduler wrapper for reserved pair; its header sets the resource limits. |
| [s76_summarize_pair_reserved.py](s76_summarize_pair_reserved.py) | Summarize every frozen trial, preserving failures and grouped paired timing. |
| [s77_audit_final.sh](s77_audit_final.sh) | Scheduler wrapper for audit final; its header sets the resource limits. |
| [s78_freeze_pair.sh](s78_freeze_pair.sh) | Scheduler wrapper for freeze pair; its header sets the resource limits. |
| [s79_run_application.py](s79_run_application.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s80_workflow_application.py](s80_workflow_application.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s81_reduce.py](s81_reduce.py) | Reduces new targets with a known master basis; reference answers are optional. |
| [s82_check_application.py](s82_check_application.py) | Check real basis-only reductions against reference answers after execution. |
| [s83_check_application.sh](s83_check_application.sh) | Scheduler wrapper for check application; its header sets the resource limits. |
| [s84_document_pair.py](s84_document_pair.py) | Document the unchanged-choice shortcut and the usable basis-only interface. |
| [s85_plot_pair.py](s85_plot_pair.py) | Plot complete and forward-stage costs after the two-row shortcut. |
| [s86_run_shared.py](s86_run_shared.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s87_workflow_shared.py](s87_workflow_shared.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s88_reduce.py](s88_reduce.py) | Reduces new targets with a known master basis; reference answers are optional. |
| [s89_build_shared.sh](s89_build_shared.sh) | Scheduler wrapper for build shared; its header sets the resource limits. |
| [s90_compare_shared.py](s90_compare_shared.py) | Compare old and shared inference with fixed weights and exact native reductions. |
| [s91_validate_shared.sh](s91_validate_shared.sh) | Scheduler wrapper for validate shared; its header sets the resource limits. |
| [s92_summarize_shared.py](s92_summarize_shared.py) | Retains all matched complete costs and independently assert unchanged decisions. |
| [s93_freeze_shared.py](s93_freeze_shared.py) | Freeze implementation-only changes after exact and timing validation. |
| [s94_confirm_shared.sh](s94_confirm_shared.sh) | Scheduler wrapper for confirm shared; its header sets the resource limits. |
| [s95_audit_shared.py](s95_audit_shared.py) | Check new exact coefficients, timing accounting and native model use. |
| [s96_finalize_shared.sh](s96_finalize_shared.sh) | Scheduler wrapper for finalize shared; its header sets the resource limits. |
| [s97_freeze_shared.sh](s97_freeze_shared.sh) | Scheduler wrapper for freeze shared; its header sets the resource limits. |
| [s98_check_shared_application.py](s98_check_shared_application.py) | Check real basis-only reductions against reference answers after execution. |
| [s99_document_shared.py](s99_document_shared.py) | Explains shared neural and row calculations using the completed comparisons. |

## Data and supporting files

- [application_verification.json](application_verification.json): This file records checks of the corresponding calculation.

- [basis_admission_fix.json](basis_admission_fix.json): Saved basis_admission_fix.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [cache_protocol.json](cache_protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [cache_resource_plan.json](cache_resource_plan.json): Saved cache_resource_plan.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [cache_summary.json](cache_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [cached_build.json](cached_build.json): Saved cached_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [database_guard_tests.json](database_guard_tests.json): Saved database_guard_tests.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [deployment.json](deployment.json): Saved deployment.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [development_summary.json](development_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [ephemeral_db_build.json](ephemeral_db_build.json): Saved ephemeral_db_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [families.json](families.json): This file defines the families in this collection.

- [fast_row_parity.json](fast_row_parity.json): Saved fast_row_parity.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [fast_rows_build.json](fast_rows_build.json): Saved fast_rows_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [final_rows_build.json](final_rows_build.json): Saved final_rows_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [integrated_validation_summary.json](integrated_validation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [modular_build.json](modular_build.json): Saved modular_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [pair_build.json](pair_build.json): Saved pair_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [pair_freeze.json](pair_freeze.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [pair_protocol.json](pair_protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [pair_report_values.json](pair_report_values.json): Saved pair_report_values.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [pair_reserved_summary.json](pair_reserved_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [pair_summary.json](pair_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [release.json](release.json): Saved release.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [report_values.json](report_values.json): Saved report_values.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [reserved_families.json](reserved_families.json): Saved reserved_families.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [runtime_config.json](runtime_config.json): Saved runtime_config.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [sparse_rows_build.json](sparse_rows_build.json): Saved sparse_rows_build.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [application_checks](application_checks/README.md).

- [cached_validation](cached_validation/README.md).

- [collection](collection/README.md).

- [control_parity](control_parity/README.md).

- [database_pilot](database_pilot/README.md).

- [fast_evaluation](fast_evaluation/README.md).

- [fast_row_parity](fast_row_parity/README.md).

- [integrated_validation](integrated_validation/README.md).

- [ordering_validation](ordering_validation/README.md).

- [pair_reserved_test](pair_reserved_test/README.md).

- [pair_validation](pair_validation/README.md).

- [pilot](pilot/README.md).

- [pilot_topological_v2](pilot_topological_v2/README.md).

- [preparation_profile](preparation_profile/README.md).

- [references](references/README.md).

- [rejected_workflows](rejected_workflows/README.md).

- [reserved_references](reserved_references/README.md).

- [reserved_test](reserved_test/README.md).

- [row_validation](row_validation/README.md).

- [scratch_pilot](scratch_pilot/README.md).

- [seed_threshold_training](seed_threshold_training/README.md).

- [shared](shared/README.md).

- [sparse_parity](sparse_parity/README.md).

- [sparse_validation](sparse_validation/README.md).

- [trajectory_training](trajectory_training/README.md).

- [trajectory_validation](trajectory_validation/README.md).

- [workflow_attempts](workflow_attempts/README.md).
