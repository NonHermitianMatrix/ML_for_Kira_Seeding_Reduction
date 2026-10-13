# cpp initial

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

[s23_cpp_model.h](s23_cpp_model.h)

The file provides native inference for the frozen source-row policy; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `cmath`, `cctype`, `cstdint`, `cstdlib`, `fstream`, `iomanip`, `map`, `set`, `sstream`, `stdexcept`, `string`, `vector`, `s24_row_weights.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s25_cpp_live_policy.h](s25_cpp_live_policy.h)

The file provides live symbolic forward-elimination experiment; GPL-3.0-or-later.

The required headers are `chrono`, `cstdio`, `cstdlib`, `fstream`, `map`, `memory`, `algorithm`, `set`, `stdexcept`, `vector`, `spawn.h`, `sys/wait.h`, `unistd.h`, `/u/home/r/rushil/ML_for_Kira_Seeding_Reduction/Kira_comparison/acceleration/s23_cpp_model.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

## Data and supporting files

- [cpp_build.json](cpp_build.json): This file contains structured records from the parent calculation.

- [cpp_build.log](cpp_build.log): This file contains saved program messages.
