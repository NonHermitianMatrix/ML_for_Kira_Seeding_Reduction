# integration

This folder supports the calculation described in the parent guide.

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

[interface.cpp.patch](interface.cpp.patch)

This patch records changes to the native Kira source.

The changed source paths are `interface.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[relations.cpp.patch](relations.cpp.patch)

This patch records changes to the native Kira source.

The changed source paths are `relations.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_early_policy.h](s00_early_policy.h)

The program predicts seed/operator relevance before constructing symbolic IBP equations.

The required headers are `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `stdexcept`, `string`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

## Data and supporting files

- [build.json](build.json): This file contains structured records from the parent calculation.
