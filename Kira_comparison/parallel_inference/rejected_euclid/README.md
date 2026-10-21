# Rejected euclid: cost of parallel prediction during Kira reduction

This folder contains the code and records for cost of parallel prediction during Kira reduction.

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
| [reduction_parallel.patch](reduction_parallel.patch) | This patch records changes to the native Kira source. |
| [s00_check_arithmetic.cpp](s00_check_arithmetic.cpp) | Exact checks for field inversion and all source-row features. |
| [s01_check_seed.py](s01_check_seed.py) | Check bitwise probabilities and masks against the preceding compiled network. |
| [s107_workflow_parallel.py](s107_workflow_parallel.py) | Run a complete fixed fallback policy; all production costs are retained. |
| [s109_build_parallel.sh](s109_build_parallel.sh) | Scheduler wrapper for build parallel; its header sets the resource limits. |
| [s110_compare_parallel.py](s110_compare_parallel.py) | Compare old and shared inference with fixed weights and exact native reductions. |
| [s112_summarize_parallel.py](s112_summarize_parallel.py) | Retains all matched complete costs and independently assert unchanged decisions. |
| [s113_freeze_parallel.py](s113_freeze_parallel.py) | Freeze exact arithmetic changes before the repeated implementation comparison. |

## Data and supporting files

- [adoption.json](adoption.json): Saved adoption.json record for cost of parallel prediction during Kira reduction; the producer code defines its fields.

- [arithmetic_check.json](arithmetic_check.json): This file records checks of the corresponding calculation.

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [seed_parity.json](seed_parity.json): Saved seed_parity.json record for cost of parallel prediction during Kira reduction; the producer code defines its fields.

- [validation_summary.json](validation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

## Child folders

- [validation](validation/README.md).
