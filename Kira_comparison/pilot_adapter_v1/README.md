# Kira timing and correctness comparisons

These records preserve development or earlier comparisons for Kira timing and correctness comparisons. They document the tested settings, including incomplete or rejected attempts.

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
| [s00_prepare.py](s00_prepare.py) | Freeze outcome-independent held-out cases, models, and resource limits. |
| [s01_common.py](s01_common.py) | Public inputs and exact coefficient arithmetic for paired Kira comparisons. |
| [s02_worker.py](s02_worker.py) | One isolated symbolic reduction, with live inference and exact fallback. |
| [s03_run.py](s03_run.py) | Run counterbalanced matched trials with bounded processes and archived evidence. |

## Data and supporting files

- [03_n01_r0_kira_native.json.gz](03_n01_r0_kira_native.json.gz): Saved 03_n01_r0_kira_native.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [03_n01_r0_kira_native_trim.json.gz](03_n01_r0_kira_native_trim.json.gz): Saved 03_n01_r0_kira_native_trim.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [03_n01_r0_kira_pool.json.gz](03_n01_r0_kira_pool.json.gz): Saved 03_n01_r0_kira_pool.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [03_n01_r0_ml_reduction.json.gz](03_n01_r0_ml_reduction.json.gz): This file records master coefficients and reduction information.

- [03_n01_r0_ml_seeds.json.gz](03_n01_r0_ml_seeds.json.gz): Saved 03_n01_r0_ml_seeds.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [04_n01_r0_kira_native.json.gz](04_n01_r0_kira_native.json.gz): Saved 04_n01_r0_kira_native.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [04_n01_r0_kira_native_trim.json.gz](04_n01_r0_kira_native_trim.json.gz): Saved 04_n01_r0_kira_native_trim.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [04_n01_r0_kira_pool.json.gz](04_n01_r0_kira_pool.json.gz): Saved 04_n01_r0_kira_pool.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [04_n01_r0_ml_reduction.json.gz](04_n01_r0_ml_reduction.json.gz): This file records master coefficients and reduction information.

- [04_n01_r0_ml_seeds.json.gz](04_n01_r0_ml_seeds.json.gz): Saved 04_n01_r0_ml_seeds.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [05_n01_r0_kira_native.json.gz](05_n01_r0_kira_native.json.gz): Saved 05_n01_r0_kira_native.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [05_n01_r0_kira_native_trim.json.gz](05_n01_r0_kira_native_trim.json.gz): Saved 05_n01_r0_kira_native_trim.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [05_n01_r0_kira_pool.json.gz](05_n01_r0_kira_pool.json.gz): Saved 05_n01_r0_kira_pool.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [05_n01_r0_ml_reduction.json.gz](05_n01_r0_ml_reduction.json.gz): This file records master coefficients and reduction information.

- [05_n01_r0_ml_seeds.json.gz](05_n01_r0_ml_seeds.json.gz): Saved 05_n01_r0_ml_seeds.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [08_n01_r0_kira_pool.json.gz](08_n01_r0_kira_pool.json.gz): Saved 08_n01_r0_kira_pool.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [08_n01_r0_ml_reduction.json.gz](08_n01_r0_ml_reduction.json.gz): This file records master coefficients and reduction information.

- [08_n01_r0_ml_seeds.json.gz](08_n01_r0_ml_seeds.json.gz): Saved 08_n01_r0_ml_seeds.json.gz record for Kira timing and correctness comparisons; the producer code defines its fields.

- [complete.json](complete.json): Completion status recorded by the experiment’s producer.

- [environment.json](environment.json): Saved environment.json record for Kira timing and correctness comparisons; the producer code defines its fields.

- [plan.json](plan.json): Saved plan.json record for Kira timing and correctness comparisons; the producer code defines its fields.

- [status.json](status.json): This file records the execution state.
