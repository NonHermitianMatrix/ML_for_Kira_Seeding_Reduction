# Selection of IBP equations

These records preserve development or earlier comparisons for selection of IBP equations. They document the tested settings, including incomplete or rejected attempts.

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
| [s00_equation_policy.h](s00_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |

## Data and supporting files

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [training_00_sunrise_n21.json.gz](training_00_sunrise_n21.json.gz): This file records training progress or training inputs.

- [training_01_sunrise_n21.json.gz](training_01_sunrise_n21.json.gz): This file records training progress or training inputs.

- [training_02_double_box_n128.json.gz](training_02_double_box_n128.json.gz): This file records training progress or training inputs.

- [training_02_double_box_n32.json.gz](training_02_double_box_n32.json.gz): This file records training progress or training inputs.

- [training_03_double_box_n32.json.gz](training_03_double_box_n32.json.gz): This file records training progress or training inputs.
