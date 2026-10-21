# Trained model: reuse of compatible equations across target batches

This folder stores the fitted models for reuse of compatible equations across target batches. Model files contain the parameters used for prediction; validation records identify the accepted choice.

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
| [forest16.c](forest16.c) | This generated C source contains the sixteen-tree prediction model. |
| [forest4.c](forest4.c) | This source file provides the compiled calculation or saved model constants. |

## Data and supporting files

- [deployment.json](deployment.json): Saved deployment.json record for reuse of compatible equations across target batches; the producer code defines its fields.

- [forest16.bin.gz](forest16.bin.gz): Saved forest16.bin.gz record for reuse of compatible equations across target batches; the producer code defines its fields.

- [forest16.json](forest16.json): Saved forest16.json record for reuse of compatible equations across target batches; the producer code defines its fields.

- [forest16.so](forest16.so): Saved forest16.so record for reuse of compatible equations across target batches; the producer code defines its fields.

- [forest4.bin.gz](forest4.bin.gz): Saved forest4.bin.gz record for reuse of compatible equations across target batches; the producer code defines its fields.

- [forest4.json](forest4.json): Saved forest4.json record for reuse of compatible equations across target batches; the producer code defines its fields.

- [forest4.so](forest4.so): Saved forest4.so record for reuse of compatible equations across target batches; the producer code defines its fields.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [native_deployment.json](native_deployment.json): Saved native_deployment.json record for reuse of compatible equations across target batches; the producer code defines its fields.

- [native_freeze.json](native_freeze.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.
