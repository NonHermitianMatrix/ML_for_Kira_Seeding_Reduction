# Development pilot: equation filtering before expensive reduction work

These records preserve development or earlier comparisons for equation filtering before expensive reduction work. They document the tested settings, including incomplete or rejected attempts.

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
| [s00_contract.py](s00_contract.py) | Exact polynomial pre-reduction of the restricted vacuum identities. |
| [s01_application.py](s01_application.py) | Pre-reduces selected exact identities, then finish and check with Kira. |
| [s02_study.py](s02_study.py) | Fresh disjoint validation and reserved comparisons of exact pre-reduction. |
| [s03_run.sh](s03_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
