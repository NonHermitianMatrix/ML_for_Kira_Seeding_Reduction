# Cpp v2: cost and implementation tests for learned reduction decisions

This folder contains the code and records for cost and implementation tests for learned reduction decisions.

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
| [s23_cpp_model.h](s23_cpp_model.h) | Native inference for the frozen source-row policy; GPL-3.0-or-later. |
| [s25_cpp_live_policy.h](s25_cpp_live_policy.h) | Live symbolic forward-elimination experiment; GPL-3.0-or-later. |

## Data and supporting files

- [cpp_build.json](cpp_build.json): Saved cpp_build.json record for cost and implementation tests for learned reduction decisions; the producer code defines its fields.
