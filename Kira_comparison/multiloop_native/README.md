# Native multiloop IBP reduction

This directory tests the models when Kira generates IBP equations from physical propagators. It measures complete reductions of specified multiloop families and preserves attempts that reach their resource limits.

The physical inputs and prescribed master bases define each request. Generated equations, final coefficients, timing records, and independent checks distinguish a completed native reduction from agreement with a stored construction path. The code sequence prepares references, runs comparisons, checks outputs, and summarizes the supported domain.

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
| [s00_storage.sh](s00_storage.sh) | Scheduler wrapper for storage; its header sets the resource limits. |
| [s01_families.py](s01_families.py) | Defines native integral families and independent targets before experiments. |
| [s02_run.py](s02_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s03_pilot.sh](s03_pilot.sh) | Scheduler wrapper for pilot; its header sets the resource limits. |
| [s04_records.py](s04_records.py) | Shares scientific evidence with atomic writes and a storage bound. |
| [s05_development.py](s05_development.py) | Collect cost labels only from the fixed training and validation cases. |
| [s06_development.sh](s06_development.sh) | Scheduler wrapper for development; its header sets the resource limits. |
| [s07_seed.py](s07_seed.py) | Applies the saved seed model to a finite native Laporta seed region. |
| [s08_workflow.py](s08_workflow.py) | Completes native workflows with bounded fallback and exact reference checks. |
| [s09_validate.py](s09_validate.py) | Measures closed-loop validation costs before reserving final test results. |
| [s10_validate.sh](s10_validate.sh) | Scheduler wrapper for validate; its header sets the resource limits. |
| [s11_rollouts.py](s11_rollouts.py) | Measures downstream algebraic work after one alternative native source choice. |
| [s12_rollouts.sh](s12_rollouts.sh) | Scheduler wrapper for rollouts; its header sets the resource limits. |
| [s13_audit_families.py](s13_audit_families.py) | Check that denominators span the independent loop scalar products. |
| [s14_worker.py](s14_worker.py) | One fresh measured workflow process; evidence writing follows the stop time. |
| [s15_fresh.py](s15_fresh.py) | Bounds the complete process, including model loading and exact verification. |
| [s16_validate_fresh.py](s16_validate_fresh.py) | Compare frozen candidate workflows in fresh validation processes. |
| [s17_validate_fresh.sh](s17_validate_fresh.sh) | Scheduler wrapper for validate fresh; its header sets the resource limits. |
| [s18_freeze.py](s18_freeze.py) | Select seed settings on validation and freeze all final scientific inputs. |
| [s19_reserved.py](s19_reserved.py) | Run the fixed, independent native multiloop comparison. |
| [s20_reserved.sh](s20_reserved.sh) | Scheduler wrapper for reserved; its header sets the resource limits. |
| [s21_seed_loader.py](s21_seed_loader.py) | Load unchanged NumPy weights with one filesystem read per archive. |
| [s22_install_runtime.py](s22_install_runtime.py) | Installs bounded per-workflow seed caches after the earlier validation jobs end. |
| [s23_prepare.sh](s23_prepare.sh) | Scheduler wrapper for prepare; its header sets the resource limits. |
| [s24_check_runtime.py](s24_check_runtime.py) | Check unchanged seed probabilities and C++/Python tree decisions. |
| [s25_analyze.py](s25_analyze.py) | Summarize every reserved outcome and form paired descriptive comparisons. |
| [s26_verify.py](s26_verify.py) | Parses exported reductions and verify exact rational coefficients. |
| [s27_analyze.sh](s27_analyze.sh) | Scheduler wrapper for analyze; its header sets the resource limits. |
| [s28_freeze.sh](s28_freeze.sh) | Scheduler wrapper for freeze; its header sets the resource limits. |
| [s29_plot.py](s29_plot.py) | Plot complete times, algebraic counts and completion including fallback. |
| [s30_plot.sh](s30_plot.sh) | Scheduler wrapper for plot; its header sets the resource limits. |
| [s31_document.py](s31_document.py) | Write result prose and numeric provenance from checked, frozen comparisons. |
| [s32_build_report.sh](s32_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |
| [s33_baseline_diagnostic.py](s33_baseline_diagnostic.py) | Post-comparison diagnostic of stock and instrumented smaller-region failures. |
| [s34_baseline_diagnostic.sh](s34_baseline_diagnostic.sh) | Scheduler wrapper for baseline diagnostic; its header sets the resource limits. |

## Data and supporting files

- [concurrency_amendment.json](concurrency_amendment.json): Saved concurrency_amendment.json record for native generation and reduction of multiloop IBP systems; the producer code defines its fields.

- [families.json](families.json): This file defines the families in this collection.

- [family_audit.json](family_audit.json): This file records checks of the corresponding calculation.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [reference_resource_amendment.json](reference_resource_amendment.json): Reference coefficients or bases used for exact comparisons.

- [report_values.json](report_values.json): Saved report_values.json record for native generation and reduction of multiloop IBP systems; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [runtime_check.json](runtime_check.json): This file records checks of the corresponding calculation.

- [scheduler_interruption.json](scheduler_interruption.json): Saved scheduler_interruption.json record for native generation and reduction of multiloop IBP systems; the producer code defines its fields.

- [storage_audit.json](storage_audit.json): This file records checks of the corresponding calculation.

- [storage_rebase.json](storage_rebase.json): Saved storage_rebase.json record for native generation and reduction of multiloop IBP systems; the producer code defines its fields.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [trials.csv](trials.csv): Saved trials.csv record for native generation and reduction of multiloop IBP systems; the producer code defines its fields.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [baseline_diagnostic](baseline_diagnostic/README.md).

- [model_test](model_test/README.md).

- [pilot](pilot/README.md).

- [pilot_v2](pilot_v2/README.md).

- [pilot_v3](pilot_v3/README.md).

- [reference_checks](reference_checks/README.md).

- [references](references/README.md).

- [reserved_references](reserved_references/README.md).

- [rollouts](rollouts/README.md).

- [runtime_checks](runtime_checks/README.md).

- [shared](shared/README.md).

- [training](training/README.md).

- [validation_final](validation_final/README.md).

- [validation_row](validation_row/README.md).

- [validation_seed](validation_seed/README.md).

- [validation_seed_safe](validation_seed_safe/README.md).
