# Before expansion 250: selection of IBP seeds

This folder contains the code and records for selection of IBP seeds.

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
| [s00_prepare_data.py](s00_prepare_data.py) | Audit seed supervision and prepare a reproducible grouped 70:30 split; it does not fit a model. |
| [s01_data.py](s01_data.py) | Streaming inputs with a strict boundary between problem features and reference labels. |
| [s02_model.py](s02_model.py) | Small shared neural scorer; every output is a reference-set membership probability. |
| [s03_train.py](s03_train.py) | Train the seed model on the training split only; save resumable and final weights here. |
| [s04_predict.py](s04_predict.py) | Ranks an input target's bounded candidate pool using an explicitly supplied trained checkpoint. |
| [s05_evaluate.py](s05_evaluate.py) | Future held-out comparison with recorded sufficient sets; no exact-reduction claim. |
| [s06_check.py](s06_check.py) | Implementation checks only: no optimizer, learned checkpoint or performance estimate. |
| [s07_run.sh](s07_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s08_setup_environment.sh](s08_setup_environment.sh) | Scheduler wrapper for setup environment; its header sets the resource limits. |
| [s09_check_training_inputs.py](s09_check_training_inputs.py) | Check training input reuse and resume ordering without evaluating the test split. |
| [s10_finalize_training.py](s10_finalize_training.py) | Verify the saved training artifact and update status documentation; never run testing. |
| [s11_run_training.sh](s11_run_training.sh) | Scheduler wrapper for run training; its header sets the resource limits. |
| [s12_prepare_features.py](s12_prepare_features.py) | Prepare bounded immutable features using training families only. |
| [s13_batch.py](s13_batch.py) | Masked batch execution of the existing seed scorer, with identical features and weights. |
| [s14_train_all_loops.py](s14_train_all_loops.py) | Continues saved weights and optimizer for twenty complete passes over expanded training data. |
| [s15_run_all_loops.sh](s15_run_all_loops.sh) | Scheduler wrapper for run all loops; its header sets the resource limits. |
| [s16_validate_all_loops.py](s16_validate_all_loops.py) | Validates the expanded-data checkpoint and preserve its training provenance. |
| [s17_run_batch_pilot.sh](s17_run_batch_pilot.sh) | Scheduler wrapper for run batch pilot; its header sets the resource limits. |
| [s18_validate_mixed_batches.py](s18_validate_mixed_batches.py) | Check batched seed scores and derivatives on mixed-length training examples. |
| [s19_run_batch_validation.sh](s19_run_batch_validation.sh) | Scheduler wrapper for run batch validation; its header sets the resource limits. |

## Data and supporting files

- [config.json](config.json): This file sets the model or calculation options.

- [data_audit.json](data_audit.json): This file records checks of the corresponding calculation.

- [release_manifest.json](release_manifest.json): This file identifies the saved release files.

- [source_hashes.json](source_hashes.json): Saved source_hashes.json record for selection of IBP seeds; the producer code defines its fields.

- [split_manifest.json](split_manifest.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [data](data/README.md).

- [runs](runs/README.md).
