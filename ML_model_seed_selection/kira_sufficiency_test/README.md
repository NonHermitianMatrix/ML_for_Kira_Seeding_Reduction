# Seed sufficiency tests

These tests ask whether the original neural seed model supplies enough equations to reduce each target to its required master basis. They compare selected equations with the complete candidate pool and preserve incomplete reductions.

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
| [s00_check_kira.py](s00_check_kira.py) | Small exact Kira fixtures before testing predicted seed sets. |
| [s01_run_fixtures.sh](s01_run_fixtures.sh) | Scheduler wrapper for run fixtures; its header sets the resource limits. |
| [s02_common.py](s02_common.py) | Frozen inputs, bounded exact rational arithmetic, and seed-filtered systems. |
| [s03_kira_adapter.py](s03_kira_adapter.py) | Export disjoint seed selections and read Kira's exact symbolic reductions. |
| [s04_run_pilot.py](s04_run_pilot.py) | Run bounded mathematical checks and representative held-out Kira reductions. |
| [s05_run_pilot.sh](s05_run_pilot.sh) | Scheduler wrapper for run pilot; its header sets the resource limits. |
| [s06_evaluate.py](s06_evaluate.py) | Freeze the solver protocol and evaluate disjoint held-out systems on Hoffman. |
| [s07_run_evaluation.sh](s07_run_evaluation.sh) | Scheduler wrapper for run evaluation; its header sets the resource limits. |
| [s08_verify.py](s08_verify.py) | Independent finite-field checks, using a nonrecursive rational-expression reader. |
| [s09_check_import.py](s09_check_import.py) | Check supported symbolic-system import modes on the small legacy-family pilot. |
| [s10_run_import_checks.sh](s10_run_import_checks.sh) | Scheduler wrapper for run import checks; its header sets the resource limits. |
| [s11_summarize.py](s11_summarize.py) | Validates saved solver records, then summarize exact target completion. |
| [s12_run_summary.sh](s12_run_summary.sh) | Scheduler wrapper for run summary; its header sets the resource limits. |
| [s13_plot_results.py](s13_plot_results.py) | Plot exact seed sufficiency and the selected candidate fractions. |
| [s14_run_plots.sh](s14_run_plots.sh) | Scheduler wrapper for run plots; its header sets the resource limits. |
| [s15_update_report.py](s15_update_report.py) | Updates the scientific report from the completed Kira sufficiency test. |
| [s16_check_target_order.py](s16_check_target_order.py) | Check direct target ordering without changing seeds or source identities. |
| [s17_run_ordering_check.sh](s17_run_ordering_check.sh) | Scheduler wrapper for run ordering check; its header sets the resource limits. |
| [s18_check_master_span.py](s18_check_master_span.py) | Test exact membership in the span of identities and specified masters. |
| [s19_run_span_check.sh](s19_run_span_check.sh) | Scheduler wrapper for run span check; its header sets the resource limits. |
| [s20_validate_span_pilot.py](s20_validate_span_pilot.py) | Validates exact master-span decisions independently before the full run. |
| [s21_run_span_validation.sh](s21_run_span_validation.sh) | Scheduler wrapper for run span validation; its header sets the resource limits. |
| [s22_coefficient_reader.py](s22_coefficient_reader.py) | Bounded, nonrecursive parsing of Kira rational expressions. |
| [s23_check_quotient_order.py](s23_check_quotient_order.py) | Bounded diagnostic of equivalent target-first quotient ordering. |
| [s24_run_quotient_order.sh](s24_run_quotient_order.sh) | Scheduler wrapper for run quotient order; its header sets the resource limits. |
| [s25_finalize_readmes.py](s25_finalize_readmes.py) | Write completion descriptions only from independently validated test results. |
| [s26_validate_reader.py](s26_validate_reader.py) | Check the large-expression reader against the archived independent evaluator. |
| [s27_retry_small_batches.py](s27_retry_small_batches.py) | Retries unresolved symbolic systems with independent, smaller target batches. |
| [s28_run_small_batch_pilot.sh](s28_run_small_batch_pilot.sh) | Scheduler wrapper for run small batch pilot; its header sets the resource limits. |
| [s29_resume_small_batches.py](s29_resume_small_batches.py) | Resumes the same frozen test with smaller box-family execution batches. |
| [s30_run_small_batches.sh](s30_run_small_batches.sh) | Scheduler wrapper for run small batches; its header sets the resource limits. |
| [s31_pack_small_batches.py](s31_pack_small_batches.py) | Packs at most four independent small systems while preserving all equations. |
| [s32_verify_export.py](s32_verify_export.py) | Regenerates each actual Kira input from public targets and selected identities. |
| [s33_output_budget.py](s33_output_budget.py) | Bounds compressed writes to a documented 32 MiB worker allowance. |
| [s34_resume_output_budget.py](s34_resume_output_budget.py) | Resumes completed or stopped shards within the revised storage reserve. |
| [s35_run_output_resume.sh](s35_run_output_resume.sh) | Scheduler wrapper for run output resume; its header sets the resource limits. |
| [s36_resume_unfinished.py](s36_resume_unfinished.py) | Finishes only shards left incomplete after the preceding execution. |
| [s37_run_remaining.sh](s37_run_remaining.sh) | Scheduler wrapper for run remaining; its header sets the resource limits. |
| [s38_output_budget_48.py](s38_output_budget_48.py) | Bounds compressed writes to a documented 48 MiB worker allowance. |
| [s39_resume_output_48.py](s39_resume_output_48.py) | Resumes completed or stopped shards within the revised storage reserve. |
| [s40_finish_remaining.py](s40_finish_remaining.py) | Finishes only shards left incomplete after the preceding execution. |
| [s41_run_remaining.sh](s41_run_remaining.sh) | Scheduler wrapper for run remaining; its header sets the resource limits. |
| [s42_resume_ready.py](s42_resume_ready.py) | Use spare slots for finished shards while other earlier shards continue. |
| [s43_run_ready.sh](s43_run_ready.sh) | Scheduler wrapper for run ready; its header sets the resource limits. |
| [s44_output_budget_80.py](s44_output_budget_80.py) | Bounds compressed writes to a documented 80 MiB worker allowance. |
| [s45_resume_large_output.py](s45_resume_large_output.py) | Resumes completed or stopped shards within the revised storage reserve. |
| [s46_run_large_output.sh](s46_run_large_output.sh) | Scheduler wrapper for run large output; its header sets the resource limits. |

## Data and supporting files

- [execution_overrides.json](execution_overrides.json): Saved execution_overrides.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [family_results.csv](family_results.csv): Saved family_results.csv record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [fixture_runs.json](fixture_runs.json): Saved fixture_runs.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [fixture_scheduler.log](fixture_scheduler.log): This file contains saved program messages.

- [import_scheduler.log](import_scheduler.log): This file contains saved program messages.

- [input_regeneration_pilot.json](input_regeneration_pilot.json): Saved input_regeneration_pilot.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [ordering_scheduler.log](ordering_scheduler.log): This file contains saved program messages.

- [packing_validation.json](packing_validation.json): Recorded checks of the calculation, data, or selected settings.

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

- [plot_scheduler.log](plot_scheduler.log): This file contains saved program messages.

- [protocol.json](protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [quotient_ordering_scheduler.log](quotient_ordering_scheduler.log): This file contains saved program messages.

- [reader_validation.json](reader_validation.json): Recorded checks of the calculation, data, or selected settings.

- [ready_resume_schedule.json](ready_resume_schedule.json): Saved ready_resume_schedule.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [resource_limits.json](resource_limits.json): Saved resource_limits.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [resource_limits_v2.json](resource_limits_v2.json): Saved resource_limits_v2.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [resource_limits_v3.json](resource_limits_v3.json): Saved resource_limits_v3.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [results.json](results.json): Saved results.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [small_batch_scheduler.log](small_batch_scheduler.log): This file contains saved program messages.

- [span_scheduler.log](span_scheduler.log): This file contains saved program messages.

- [span_validation_scheduler.log](span_validation_scheduler.log): This file contains saved program messages.

- [summary_scheduler.log](summary_scheduler.log): This file contains saved program messages.

- [validation.json](validation.json): This file records the completed validation checks.

- [worker_00.json](worker_00.json): Saved worker_00.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_01.json](worker_01.json): Saved worker_01.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_02.json](worker_02.json): Saved worker_02.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_03.json](worker_03.json): Saved worker_03.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_04.json](worker_04.json): Saved worker_04.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_05.json](worker_05.json): Saved worker_05.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_06.json](worker_06.json): Saved worker_06.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_07.json](worker_07.json): Saved worker_07.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_08.json](worker_08.json): Saved worker_08.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_09.json](worker_09.json): Saved worker_09.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_10.json](worker_10.json): Saved worker_10.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_11.json](worker_11.json): Saved worker_11.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_12.json](worker_12.json): Saved worker_12.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_13.json](worker_13.json): Saved worker_13.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_14.json](worker_14.json): Saved worker_14.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

- [worker_15.json](worker_15.json): Saved worker_15.json record for exact sufficiency of the neural model’s selected seeds; the producer code defines its fields.

## Child folders

- [archive_coefficient_reductions](archive_coefficient_reductions/README.md).

- [archive_output_allowance](archive_output_allowance/README.md).

- [archive_output_allowance_v2](archive_output_allowance_v2/README.md).

- [archive_output_allowance_v3](archive_output_allowance_v3/README.md).

- [archive_span_large_batches](archive_span_large_batches/README.md).

- [archive_span_reader_v1](archive_span_reader_v1/README.md).

- [figures](figures/README.md).

- [import_checks](import_checks/README.md).

- [ordering_pilot](ordering_pilot/README.md).

- [pilot](pilot/README.md).

- [results](results/README.md).

- [scheduler](scheduler/README.md).

- [small_batch_pilot](small_batch_pilot/README.md).

- [span_pilot](span_pilot/README.md).
