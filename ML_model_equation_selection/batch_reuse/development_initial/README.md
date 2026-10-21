# Development initial: reuse of compatible equations across target batches

These records preserve development or earlier comparisons for reuse of compatible equations across target batches. They document the tested settings, including incomplete or rejected attempts.

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
| [s00_common.py](s00_common.py) | Batch equation choices for the restricted, exact vacuum coefficient system. |
| [s01_train.py](s01_train.py) | Train a fast predictor of shared equation-substitution cost. |
| [s02_reduce.py](s02_reduce.py) | Kira integration with learned batch choices and shared exact checks. |
| [s03_study.py](s03_study.py) | Sequential paired fresh-case evaluation, with all calculation costs counted. |
| [s04_run.sh](s04_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
