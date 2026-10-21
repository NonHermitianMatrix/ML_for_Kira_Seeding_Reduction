# Storage scan resume: selection of IBP seeds

This folder contains the code and records for selection of IBP seeds.

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
| [s01_data_before.py](s01_data_before.py) | Streaming inputs with a strict boundary between problem features and reference labels. |

## Data and supporting files

- [checkpoint_before.pt](checkpoint_before.pt): This file contains a saved model or its description.

- [migration.json](migration.json): Saved migration.json record for selection of IBP seeds; the producer code defines its fields.

- [verification.json](verification.json): This file records the independent checks.
