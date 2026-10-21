# Reuse of compatible equations across target batches

This folder contains the code and records for reuse of compatible equations across target batches.

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
| [s00_common.py](s00_common.py) | Batch equation choices for the restricted, exact vacuum coefficient system. |
| [s01_train.py](s01_train.py) | Train a fast predictor of shared equation-substitution cost. |
| [s02_reduce.py](s02_reduce.py) | Kira integration with learned batch choices and shared exact checks. |
| [s03_study.py](s03_study.py) | Sequential paired fresh-case evaluation, with all calculation costs counted. |
| [s04_run.sh](s04_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s05_check.py](s05_check.py) | Independent arithmetic and domain checks, including equivalent loop expansions. |
| [s06_select.py](s06_select.py) | Select only on validation complete costs, then freeze before fresh tests. |
| [s07_compact.py](s07_compact.py) | Stores exactly the same trained trees in a bounded compact representation. |
| [s08_reader.py](s08_reader.py) | Fast exact integer-polynomial reader with the previous rational reader as fallback. |
| [s09_application.py](s09_application.py) | Public entry point for the frozen, validated batch reduction deployment. |
| [s10_analyze.py](s10_analyze.py) | Fresh-case complete times and independent exact audits of saved reductions. |
| [s11_pack.py](s11_pack.py) | Reduces several independent mass profiles in one exact Kira system. |
| [s12_pack_study.py](s12_pack_study.py) | Paired packed/separate applications, preserving identical targets and checks. |
| [s13_run.sh](s13_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s14_pack_analyze.py](s14_pack_analyze.py) | Audit every saved packed result against the independent original loop oracle. |
| [s15_integration.py](s15_integration.py) | Check production entry points, extended loop values and exact fallback. |
| [s16_native.py](s16_native.py) | Compiles unchanged trained trees and compare all scores exactly. |
| [s17_application.py](s17_application.py) | Applies identical learned choices through a native inference library. |
| [s18_native_study.py](s18_native_study.py) | Fresh native-inference validation followed by frozen independent confirmation. |
| [s19_run.sh](s19_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s20_native_analyze.py](s20_native_analyze.py) | Audit native-backend confirmation and compare full applications. |
| [s21_plot.py](s21_plot.py) | Reproducible figures of complete exact application times. |
| [s22_document.py](s22_document.py) | Write report and READMEs from audited complete calculation results. |
| [s23_release_check.py](s23_release_check.py) | Releases guards for exactness, unchanged earlier studies and the storage ceiling. |
| [s24_native_application_check.py](s24_native_application_check.py) | Check the final public deployment and compiled backend at extended loop orders. |

## Data and supporting files

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for reuse of compatible equations across target batches; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

## Child folders

- [development_initial](development_initial/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
