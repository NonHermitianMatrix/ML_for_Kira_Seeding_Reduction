# trained model

This folder contains saved model parameters or candidate methods.
Use the parent validation record to identify the selected method.

Read [the parent guide](../README.md) for the stage and data flow.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Code files

The entries below follow file-name order.
Each entry gives its purpose and the input or output interface available in the source.

[forest16.c](forest16.c)

This generated C source contains the sixteen-tree prediction model.
The parent `s16_native.py` script writes, compiles and loads it.
Its `predict` function accepts up to 24 rows with 32 double-precision features per row.
It writes one mean tree score per row.
The build uses GCC with `-O2 -std=c99 -shared -fPIC`.
The source generator checks scores against the saved Python trees.

[forest4.c](forest4.c)

This source file provides the compiled calculation or saved model constants.

The required headers are `stddef.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

## Data and supporting files

- [deployment.json](deployment.json): This file contains structured records from the parent calculation.

- [forest16.bin.gz](forest16.bin.gz): This archive contains saved records for the parent calculation.

- [forest16.json](forest16.json): This file contains structured records from the parent calculation.

- [forest16.so](forest16.so): This file supports the calculation described in the parent guide.

- [forest4.bin.gz](forest4.bin.gz): This archive contains saved records for the parent calculation.

- [forest4.json](forest4.json): This file contains structured records from the parent calculation.

- [forest4.so](forest4.so): This file supports the calculation described in the parent guide.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [native_deployment.json](native_deployment.json): This file contains structured records from the parent calculation.

- [native_freeze.json](native_freeze.json): This file contains structured records from the parent calculation.
