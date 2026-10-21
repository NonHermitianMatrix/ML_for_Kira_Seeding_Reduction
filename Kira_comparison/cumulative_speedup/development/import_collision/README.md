# Import collision: exact vacuum recurrence compared with supplied-equation Kira

This folder contains the code and records for exact vacuum recurrence compared with supplied-equation Kira.

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
| [s00_common.py](s00_common.py) | Shared paths, frozen provenance, bounded resources and coefficient output. |
| [s01_cases.py](s01_cases.py) | Declares independent matched requests without fitting any policy. |
| [s02_worker.py](s02_worker.py) | Run a complete matched reduction and save lossless exact coefficients. |
| [s03_study.py](s03_study.py) | Executes paired frozen comparisons with resource monitoring. |
| [s04_run.sh](s04_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |

## Data and supporting files

- [scheduler.log](scheduler.log): This file contains saved program messages.
