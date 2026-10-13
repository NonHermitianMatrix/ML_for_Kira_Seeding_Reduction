# binding request

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

[s10_parallel.py](s10_parallel.py)

The program runs independent paired groups on four explicitly allocated physical cores.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_cumulative`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(p / 'physical_package_id').read_text()
(p / 'core_id').read_text()

```

## Data and supporting files

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [protocol.json](protocol.json): This file contains structured records from the parent calculation.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.
