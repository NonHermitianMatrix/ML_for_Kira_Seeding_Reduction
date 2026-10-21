# Restricted vacuum reductions across loop orders

This folder contains the code and records for restricted vacuum reductions across loop orders.

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
| [s00_math.py](s00_math.py) | Exact restricted vacuum identities and coefficient-free dependency choices. |
| [s01_train.py](s01_train.py) | Train small equation-choice trees from exact dependency counts. |
| [s02_reduce.py](s02_reduce.py) | Generate a sufficient equation system, run bounded Kira and check exact coefficients. |
| [s03_cases.py](s03_cases.py) | Create distinct mass profiles and exponent batches before fitting or timing. |
| [s04_study.py](s04_study.py) | Run predeclared comparisons in sequential bounded worker processes. |
| [s05_run.sh](s05_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s06_select.py](s06_select.py) | Chooses policies on validation measurements and freeze before reserved tests. |
| [s07_analyze.py](s07_analyze.py) | Audit exact test exports and summarize the frozen paired costs. |
| [s08_application.py](s08_application.py) | Applies the frozen higher-loop deployment to a new supported family request. |
| [s09_plot.py](s09_plot.py) | Makes standalone figures from the frozen higher-loop cost audit. |
| [s10_polynomial.py](s10_polynomial.py) | Bounded exact reading of Kira's univariate rational coefficients. |
| [s11_reader_audit.py](s11_reader_audit.py) | Cross-checks a fast exact coefficient reader against symbolic algebra. |
| [s12_document.py](s12_document.py) | Document only verified higher-loop measurements and the selected deployment. |
| [s13_release_check.py](s13_release_check.py) | Check release integrity, existing-data applications and storage bounds. |
| [s14_extrapolate.py](s14_extrapolate.py) | Check the frozen application at additional loop orders above the timing set. |
| [s16_export_existing.py](s16_export_existing.py) | Prepare scalar-component requests from the existing coupled vacuum dataset. |

## Data and supporting files

- [design.json](design.json): Saved design.json record for restricted vacuum reductions across loop orders; the producer code defines its fields.

- [pipeline_scheduler.log](pipeline_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for restricted vacuum reductions across loop orders; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

## Child folders

- [development_initial](development_initial/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
