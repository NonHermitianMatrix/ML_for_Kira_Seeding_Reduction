# Integration: native integration and build procedures

This folder contains the code and records for native integration and build procedures.

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
| [interface.cpp.patch](interface.cpp.patch) | This patch records changes to the native Kira source. |
| [relations.cpp.patch](relations.cpp.patch) | This patch records changes to the native Kira source. |
| [s00_early_policy.h](s00_early_policy.h) | Predicts seed/operator relevance before constructing symbolic IBP equations. |

## Data and supporting files

- [build.json](build.json): Compiler, source, and executable information from the recorded build.
