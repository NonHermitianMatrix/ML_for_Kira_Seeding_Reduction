# Shared evaluation of target expressions

This folder contains the code and records for shared evaluation of target expressions.

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
| [connect2kira.patch](connect2kira.patch) | This patch records changes to the native Kira source. |
| [s00_prepare.py](s00_prepare.py) | Fixs new timing cases and resource limits before measuring the new interface. |
| [s01_reap_child.h](s01_reap_child.h) | SPDX-License-Identifier: GPL-3.0-or-later. |
| [s02_reap_test.cpp](s02_reap_test.cpp) | SPDX-License-Identifier: GPL-3.0-or-later. |
| [s03_build.py](s03_build.py) | Build an isolated stock Kira with responsive, bounded Fermat shutdown. |
| [s04_build.sh](s04_build.sh) | Scheduler wrapper for build; its header sets the resource limits. |
| [s05_worker.py](s05_worker.py) | Run unchanged seed selection and exact checks with a chosen Kira binary. |
| [s06_run.py](s06_run.py) | Rotates complete cold trials and retain failures within fixed resource limits. |
| [s07_development.sh](s07_development.sh) | Scheduler wrapper for development; its header sets the resource limits. |
| [s08_freeze.py](s08_freeze.py) | Freeze all scientific inputs and executables after development checks. |
| [s09_test_array.sh](s09_test_array.sh) | Scheduler wrapper for test array; its header sets the resource limits. |
| [s10_audit.py](s10_audit.py) | Check raw Kira coefficients and unchanged seed decisions. |
| [s11_summary.py](s11_summary.py) | Reports all completions and group-resampled paired complete-time ratios. |
| [s12_check.sh](s12_check.sh) | Scheduler wrapper for check; its header sets the resource limits. |
| [s13_records.py](s13_records.py) | Lossless shared arrays keep repeated timing evidence within the storage cap. |
| [s14_report.py](s14_report.py) | Write measured results, a figure and the scientific report after validation. |
| [s15_confirm.sh](s15_confirm.sh) | Scheduler wrapper for confirm; its header sets the resource limits. |
| [s16_document.py](s16_document.py) | Updates the experiment and project READMEs from audited results. |
| [s17_build_report.sh](s17_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |
| [s18_release.py](s18_release.py) | Check frozen inputs, all trial records, resource bounds and release readiness. |
| [s19_finalize.sh](s19_finalize.sh) | Scheduler wrapper for finalize; its header sets the resource limits. |
| [s20_report_finish.py](s20_report_finish.py) | Applies final report formatting and state the measured completion cohorts. |
| [s21_report_compat.py](s21_report_compat.py) | Renders the frozen report script with the cluster Matplotlib API. |

## Data and supporting files

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [development_summary.json](development_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [development_validation.json](development_validation.json): Recorded checks of the calculation, data, or selected settings.

- [execution.json](execution.json): Saved execution.json record for shared evaluation of target expressions; the producer code defines its fields.

- [figure_values.csv](figure_values.csv): Saved figure_values.csv record for shared evaluation of target expressions; the producer code defines its fields.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [plan.json](plan.json): Saved plan.json record for shared evaluation of target expressions; the producer code defines its fields.

- [reap_validation.json](reap_validation.json): Recorded checks of the calculation, data, or selected settings.

- [release_validation.json](release_validation.json): Recorded checks of the calculation, data, or selected settings.

- [report_values.json](report_values.json): Saved report_values.json record for shared evaluation of target expressions; the producer code defines its fields.

- [scheduler_amendment.json](scheduler_amendment.json): Saved scheduler_amendment.json record for shared evaluation of target expressions; the producer code defines its fields.

- [scheduler_amendment_02.json](scheduler_amendment_02.json): Saved scheduler_amendment_02.json record for shared evaluation of target expressions; the producer code defines its fields.

- [test_summary.json](test_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [test_validation.json](test_validation.json): Recorded checks of the calculation, data, or selected settings.

## Child folders

- [development](development/README.md).

- [evidence](evidence/README.md).

- [shared](shared/README.md).

- [test](test/README.md).
