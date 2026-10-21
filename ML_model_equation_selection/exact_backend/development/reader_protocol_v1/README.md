# Reader protocol v1: exact recurrences for the restricted coupled-vacuum family

This folder contains the code and records for exact recurrences for the restricted coupled-vacuum family.

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
| [s15_application.py](s15_application.py) | Public interface for the validated arithmetic and compiled-reader extension. |
| [s16_reader_study.py](s16_reader_study.py) | Fresh validation and reserved tests for the compiled coefficient reader. |

## Data and supporting files

- [reader_deployment.json](reader_deployment.json): Saved reader_deployment.json record for exact recurrences for the restricted coupled-vacuum family; the producer code defines its fields.

- [reader_freeze.json](reader_freeze.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_protocol.json](reader_protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [reader_scheduler.log](reader_scheduler.log): This file contains saved program messages.
