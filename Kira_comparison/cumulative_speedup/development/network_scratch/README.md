# network scratch

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

[s03_study.py](s03_study.py)

The program executes paired frozen comparisons with resource monitoring.

The module defines these callable interfaces:

```python

def trial(inp, arm, rep, folder)
def main()

```

The imported project modules are `s00_cumulative`.

The command accepts these parser options:

- `'stage'`: choices=['pilot', 'freeze', 'test'].

These calls show the stored input and output interface:

```python

Path('/proc/cpuinfo').read_text()

```

## Data and supporting files

- [cleanup.json](cleanup.json): This file contains structured records from the parent calculation.

- [environment.json](environment.json): This file contains structured records from the parent calculation.

- [leftover_kira_high_xxnr18em.log](leftover_kira_high_xxnr18em.log): This file contains saved program messages.

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

## Child folders

- [results](results/README.md).
