# immediate cost v1

This folder retains an earlier stage, development check or saved comparison.
Use its records to interpret that stage.
Use the current parent application for a new calculation.

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

[reduction_cost.patch](reduction_cost.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_cost_policy.h](s00_cost_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

## Data and supporting files

- [build.json](build.json): This file contains structured records from the parent calculation.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_weights.txt](trained_weights.txt): This file contains a saved model or its description.

- [training_results.json](training_results.json): This file records training progress or training inputs.
