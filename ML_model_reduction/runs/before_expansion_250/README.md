# Before expansion 250: selection of elimination steps

This folder contains the code and records for selection of elimination steps.

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
| [s00_common.py](s00_common.py) | Paths, bounded storage and reproducible file operations. |
| [s01_state.py](s01_state.py) | Encodes current matrix/actions and apply exact finite-field elementary row operations. |
| [s02_prepare_data.py](s02_prepare_data.py) | Prepare only the existing training-family reduction states; replay every label. |
| [s03_model.py](s03_model.py) | Shared 32-component candidate encoder with pooled candidate context. |
| [s04_train.py](s04_train.py) | Train all prepared choice states, with deterministic group-boundary resume. |
| [s05_predict.py](s05_predict.py) | Returns all next-step probabilities; optionally apply the selected exact row operation. |
| [s06_check.py](s06_check.py) | Analytical and training-only checks; no held-out dataset is opened. |
| [s07_run_training.sh](s07_run_training.sh) | Scheduler wrapper for run training; its header sets the resource limits. |
| [s08_finalize.py](s08_finalize.py) | Verify trained artifacts and write completed-training report text; no held-out evaluation. |
| [s09_finalize_report.sh](s09_finalize_report.sh) | Scheduler wrapper for finalize report; its header sets the resource limits. |
| [s10_train_all_loops.py](s10_train_all_loops.py) | Warm-start the saved reduction model and optimizer for twenty expanded-data passes. |
| [s11_run_all_loops.sh](s11_run_all_loops.sh) | Scheduler wrapper for run all loops; its header sets the resource limits. |

## Data and supporting files

- [config.json](config.json): This file sets the model or calculation options.

- [release_manifest.json](release_manifest.json): This file identifies the saved release files.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [data](data/README.md).

- [runs](runs/README.md).
