# Reuse of exact coefficient polynomials

This experiment shares coefficient polynomials across compatible reductions of the restricted vacuum family. The model and fixed controls select computational choices, while exact polynomial operations determine the coefficients.

The producers define the requested mass profiles, target powers, and loop orders. Saved records contain coefficient representations, exact checks, and complete timing costs. Preserve the family assumptions when reusing coefficients; a matching loop count alone does not establish an equivalent integral.

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
| [s00_arithmetic.py](s00_arithmetic.py) | Shared exact Taylor terms and integer loop-order transformations. |
| [s01_engine.py](s01_engine.py) | Preserves exact reduction and verification while reusing arithmetic work. |
| [s02_application.py](s02_application.py) | Single-request and bounded persistent-worker interfaces. |
| [s03_check.py](s03_check.py) | Independent arithmetic and persistent-interface checks. |
| [s04_study.py](s04_study.py) | Fresh validation and reserved single-request and stream comparisons. |
| [s05_run.sh](s05_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s06_audit.py](s06_audit.py) | Audit stored exact results against the older loop-dependent formula. |
| [s07_analyze.py](s07_analyze.py) | Separates arithmetic and process-reuse effects in the complete measurements. |
| [s08_plot.py](s08_plot.py) | Export standalone figures for exact arithmetic and persistent processing. |
| [s09_document.py](s09_document.py) | Updates the report and READMEs from frozen arithmetic-reuse measurements. |
| [s10_release_check.py](s10_release_check.py) | Check frozen methods, exact evidence, report references and resource bounds. |
| [s11_finish.sh](s11_finish.sh) | Scheduler wrapper for finish; its header sets the resource limits. |

## Data and supporting files

- [audit_scheduler.log](audit_scheduler.log): This file records checks of the corresponding calculation.

- [deployment.json](deployment.json): Saved deployment.json record for reuse of symbolic coefficient polynomials; the producer code defines its fields.

- [final_report_scheduler.log](final_report_scheduler.log): This file contains saved program messages.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [report_scheduler.log](report_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for reuse of symbolic coefficient polynomials; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [validation](validation/README.md).
