# Binding request: exact vacuum recurrence compared with supplied-equation Kira

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
| [s10_parallel.py](s10_parallel.py) | Run independent paired groups on four explicitly allocated physical cores. |

## Data and supporting files

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [protocol.json](protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.
