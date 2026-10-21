# Reserved model tests

These reserved tests replay elimination choices on constructed targets. Predictions, trajectories, and operation counts describe that test setting. Native Kira timing experiments are separate, and the deployed application omits this row model.

This folder contains reserved test inputs, outputs or checks.
Keep these records outside model fitting and threshold selection.

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
| [s00_test_common.py](s00_test_common.py) | Shared held-out metrics, bounded outputs and exact sample arithmetic. |
| [s01_policies.py](s01_policies.py) | Autonomous target-row policies and exact checks at independent stored samples. |
| [s02_evaluate.py](s02_evaluate.py) | Frozen held-out reference-state and autonomous reduction evaluation. |
| [s03_check_metrics.py](s03_check_metrics.py) | Independent analytical checks before evaluating held-out families. |
| [s04_run_test.sh](s04_run_test.sh) | Scheduler wrapper for run test; its header sets the resource limits. |
| [s05_validate_outputs.py](s05_validate_outputs.py) | Independent checks of saved predictions and complete finite-field trajectories. |
| [s06_plot_results.py](s06_plot_results.py) | Generate six report figures from fixed saved held-out results. |
| [s07_update_report.py](s07_update_report.py) | Updates the reduction training and held-out sections from independently checked records. |
| [s08_finalize_report.sh](s08_finalize_report.sh) | Scheduler wrapper for finalize report; its header sets the resource limits. |
| [s09_validate_checkpoint.py](s09_validate_checkpoint.py) | Validates twenty expanded-data passes and freeze the exact checkpoint for testing. |
| [s10_parallel_test.py](s10_parallel_test.py) | Evaluates disjoint held-out families on four allocated CPU slots, then aggregate. |
| [s11_validate_trained.sh](s11_validate_trained.sh) | Scheduler wrapper for validate trained; its header sets the resource limits. |
| [s12_finalize_test.sh](s12_finalize_test.sh) | Scheduler wrapper for finalize test; its header sets the resource limits. |

## Data and supporting files

- [checkpoint_validation.json](checkpoint_validation.json): This file records checks of the corresponding calculation.

- [confidence_reliability.csv](confidence_reliability.csv): Saved confidence_reliability.csv record for selection of elimination steps; the producer code defines its fields.

- [family_metrics.csv](family_metrics.csv): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [family_metrics.json](family_metrics.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [figure_manifest.json](figure_manifest.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [figure_values.csv](figure_values.csv): Saved figure_values.csv record for selection of elimination steps; the producer code defines its fields.

- [finalize_scheduler.log](finalize_scheduler.log): This file contains saved program messages.

- [finalize_scheduler_before_storage_guard.log](finalize_scheduler_before_storage_guard.log): This file contains saved program messages.

- [metric_checks.json](metric_checks.json): This file records checks of the corresponding calculation.

- [paired_comparison.json](paired_comparison.json): Saved paired_comparison.json record for selection of elimination steps; the producer code defines its fields.

- [parallel_execution.json](parallel_execution.json): Saved parallel_execution.json record for selection of elimination steps; the producer code defines its fields.

- [pilot.json](pilot.json): Saved pilot.json record for selection of elimination steps; the producer code defines its fields.

- [report_template.tex](report_template.tex): This file contains a LaTeX document or document section.

- [report_values.json](report_values.json): Saved report_values.json record for selection of elimination steps; the producer code defines its fields.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [scheduler_before_storage_guard.log](scheduler_before_storage_guard.log): This file contains saved program messages.

- [status.json](status.json): This file records the execution state.

- [target_metrics.jsonl.gz](target_metrics.jsonl.gz): This file records the target definitions or target identifiers.

- [test_config.json](test_config.json): Saved test_config.json record for selection of elimination steps; the producer code defines its fields.

- [test_results.json](test_results.json): Saved test_results.json record for selection of elimination steps; the producer code defines its fields.

- [tie_metrics.json](tie_metrics.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [training_section_template.tex](training_section_template.tex): This file records training progress or training inputs.

- [validation.json](validation.json): This file records the completed validation checks.

- [validation_status.json](validation_status.json): This file records the execution state.

- [worker_00.log](worker_00.log): This file contains saved program messages.

- [worker_00_status.json](worker_00_status.json): This file records the execution state.

- [worker_01.log](worker_01.log): This file contains saved program messages.

- [worker_01_status.json](worker_01_status.json): This file records the execution state.

- [worker_02.log](worker_02.log): This file contains saved program messages.

- [worker_02_status.json](worker_02_status.json): This file records the execution state.

- [worker_03.log](worker_03.log): This file contains saved program messages.

- [worker_03_status.json](worker_03_status.json): This file records the execution state.

## Child folders

- [archive_before_all_loops](archive_before_all_loops/README.md).

- [archive_before_expansion_250](archive_before_expansion_250/README.md).

- [families](families/README.md).

- [figures](figures/README.md).
