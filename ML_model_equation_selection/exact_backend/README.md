# Exact recurrence for restricted vacuum integrals

This experiment replaces repeated supplied-equation reductions of the restricted coupled-vacuum family with exact coefficient calculations. The massive denominators share a loop-momentum sum. Integer-polynomial representations and shared coefficients avoid repeating equivalent symbolic work.

The application accepts the family and target settings documented by its producer and returns lossless coefficient records. Compiled transformations and readers use GMP. Tests compare the coefficients and full output cost with fixed arithmetic and Kira controls. These analytic gains have a restricted physical domain and do not measure generic ML acceleration.

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
| [s00_backend.py](s00_backend.py) | Exact integer polynomials, bounded binary records and legacy compatibility. |
| [s01_transform.cpp](s01_transform.cpp) | Bounded exact polynomial transformations with GMP. |
| [s02_engine.py](s02_engine.py) | Shared integer representation with compiled expansion and learned batch routing. |
| [s03_application.py](s03_application.py) | Bounded single-batch and persistent interfaces with lossless coefficient output. |
| [s04_check.py](s04_check.py) | Check exact arithmetic, binary round trips, worker isolation and Kira fallback. |
| [s05_study.py](s05_study.py) | Collect complete runtime labels, validate policies, then freeze independent tests. |
| [s06_run.sh](s06_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s07_audit.py](s07_audit.py) | Audit reserved coefficients, binary readers and fixed policies. |
| [s08_analyze.py](s08_analyze.py) | Summarize frozen complete timings, decoding costs and model comparisons. |
| [s09_plot.py](s09_plot.py) | Plot exact arithmetic, complete output costs and learned strategy results. |
| [s10_document.py](s10_document.py) | Document both frozen comparisons, the new cost model and final deployment. |
| [s11_release_check.py](s11_release_check.py) | Verify both frozen studies, exact evidence, report references and storage bounds. |
| [s12_report.sh](s12_report.sh) | Scheduler wrapper for report; its header sets the resource limits. |
| [s13_reader.cpp](s13_reader.cpp) | Lossless coefficient reader for the existing expanded binary format. |
| [s14_reader.py](s14_reader.py) | Use a compiled lossless reader without changing the first frozen implementation. |
| [s15_application.py](s15_application.py) | Public interface for the validated arithmetic and compiled-reader extension. |
| [s16_reader_study.py](s16_reader_study.py) | Fresh validation and reserved tests for the compiled coefficient reader. |
| [s17_reader_run.sh](s17_reader_run.sh) | Scheduler wrapper for reader run; its header sets the resource limits. |
| [s18_reader_audit.py](s18_reader_audit.py) | Audit reserved coefficients, binary readers and fixed policies. |
| [s19_reader_analyze.py](s19_reader_analyze.py) | Summarize frozen complete timings, decoding costs and model comparisons. |
| [s20_reader_plot.py](s20_reader_plot.py) | Plot exact arithmetic, complete output costs and learned strategy results. |
| [s21_reader_finish.sh](s21_reader_finish.sh) | Scheduler wrapper for reader finish; its header sets the resource limits. |

## Data and supporting files

- [audit_scheduler.log](audit_scheduler.log): This file records checks of the corresponding calculation.

- [build_scheduler.log](build_scheduler.log): This file contains saved program messages.

- [deployment.json](deployment.json): Saved deployment.json record for exact recurrences for the restricted coupled-vacuum family; the producer code defines its fields.

- [final_report_scheduler.log](final_report_scheduler.log): This file contains saved program messages.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [protocol.json](protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_deployment.json](reader_deployment.json): Saved reader_deployment.json record for exact recurrences for the restricted coupled-vacuum family; the producer code defines its fields.

- [reader_final_deployment.json](reader_final_deployment.json): Saved reader_final_deployment.json record for exact recurrences for the restricted coupled-vacuum family; the producer code defines its fields.

- [reader_final_freeze.json](reader_final_freeze.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_final_protocol.json](reader_final_protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_final_scheduler.log](reader_final_scheduler.log): This file contains saved program messages.

- [reader_freeze.json](reader_freeze.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_protocol.json](reader_protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_scheduler.log](reader_scheduler.log): This file contains saved program messages.

- [report_scheduler.log](report_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for exact recurrences for the restricted coupled-vacuum family; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [build](build/README.md).

- [development](development/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [reader_final_test](reader_final_test/README.md).

- [reader_test](reader_test/README.md).

- [reader_validation](reader_validation/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
