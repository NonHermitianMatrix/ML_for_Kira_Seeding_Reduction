# Elimination-step models

This directory trains and tests models that rank allowed elimination steps. It preserves constructed-state tests and later live-Kira cost experiments. The retained combined application omits learned row selection because its complete-time tests do not establish a benefit.

This model scores the allowed source-row operations at the current matrix.
It selects one operation and returns a probability for each candidate.
The exact solver applies the selected operation.
The neural model has 10,529 parameters and 132 features per action.

`trained_model.pt` contains the current neural model.
`runs/all_loops_latest.pt` retains the optimizer and resume position.
`data/` contains training states.
`model_test/` contains frozen tests and trajectories.
`cost_training/` and `runtime_training/` contain later native-cost models.
The retained production method omits learned row selection because complete-time gains remain unestablished.

`s02_prepare_data.py` replays the training states.
`s10_train_all_loops.py` continues the saved model for twenty training passes.
`s11_run_all_loops.sh` provides the scheduled job.
`s05_predict.py` supplies prediction and an optional exact modular operation.

The state input contains `prime`, family information, sparse rows, `row_roles`, `master_columns` and `actions`.
Each action contains `id`, `source_row`, `destination_row` and `pivot_indices`.
A source row must represent a zero identity.
Its pivot must be nonzero in the selected field.

Run this command from the project root:

```bash
.tools/seed-model/venv/bin/python ML_model_reduction/s05_predict.py state.json --output prediction.json
```

Add `--apply` to apply the selected operation.
The input limits are sixteen indices, 10,000 rows, 10,000 actions and 250,000 matrix entries.
Each row can contain at most 4,096 entries.

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

- [implementation_checks.json](implementation_checks.json): This file records checks of the corresponding calculation.

- [release_manifest.json](release_manifest.json): This file identifies the saved release files.

- [report_validation.json](report_validation.json): Recorded checks of the calculation, data, or selected settings.

- [requirements.txt](requirements.txt): This file lists the Python package requirements.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [cost_training](cost_training/README.md).

- [data](data/README.md).

- [model_test](model_test/README.md).

- [runs](runs/README.md).

- [runtime_training](runtime_training/README.md).

## Related application

The [combined reduction application](../ML_model_adaptive_reduction/triangle_reduction/README.md) integrates the retained exact and learned methods. The [selective-expansion experiment](../ML_model_adaptive_reduction/selective_expansion/README.md) compares candidate seed and worker settings.

## Independent component checks

The [component and higher-loop study](../Kira_comparison/higher_scattering/README.md) tests each decision with matching targets and exact checks.
It preserves the earlier models and results.
It also records connected scattering tests, initialization costs, and incomplete calculations.
Read its summary for the measured contributions and tested domain.
