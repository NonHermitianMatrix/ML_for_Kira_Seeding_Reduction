# Linear continuation v2: row policies trained on measured algebraic cost

This folder contains the code and records for row policies trained on measured algebraic cost.

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
| [reduction_cost.patch](reduction_cost.patch) | This patch records changes to the native Kira source. |

## Data and supporting files

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_weights.txt](trained_weights.txt): This file contains a saved model or its description.

- [training_results.json](training_results.json): This file records training progress or training inputs.
