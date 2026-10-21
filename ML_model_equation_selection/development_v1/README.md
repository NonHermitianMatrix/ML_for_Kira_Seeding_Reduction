# Selection of IBP equations

These records preserve development or earlier comparisons for selection of IBP equations. They document the tested settings, including incomplete or rejected attempts.

This folder retains an earlier stage, development check or saved comparison.
Use its records to interpret that stage.
Use the current parent application for a new calculation.

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
| [s00_build.py](s00_build.py) | Compiles equation filtering and collection without changing prior binaries. |
| [s00_equation_policy.h](s00_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |
| [s01_build.sh](s01_build.sh) | Scheduler wrapper for build; its header sets the resource limits. |
| [s02_records.py](s02_records.py) | Bounded compressed exact evidence. |
| [s03_run.py](s03_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s04_experiment.py](s04_experiment.py) | Collect native labels and compare frozen filters with exact fallback. |
| [s05_run.sh](s05_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s06_train.py](s06_train.py) | Fit a small target-dependent CART probability model using training groups only. |
| [s07_train.sh](s07_train.sh) | Scheduler wrapper for train; its header sets the resource limits. |
| [s08_develop.sh](s08_develop.sh) | Scheduler wrapper for develop; its header sets the resource limits. |
| [s09_predict.py](s09_predict.py) | Predicts reference-membership probabilities from the documented 24 features. |
| [s10_summarize.py](s10_summarize.py) | Summarize paired timings without dropping failed filtered attempts. |

## Data and supporting files

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [status.json](status.json): This file records the execution state.

## Child folders

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
