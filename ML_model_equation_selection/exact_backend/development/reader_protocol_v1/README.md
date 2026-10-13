# reader protocol v1

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

[s15_application.py](s15_application.py)

The file provides public interface for the validated arithmetic and compiled-reader extension.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_backend`, `s02_engine`, `s03_application`, `s14_reader`.

The command accepts these parser options:

- `'--input'`: The parser accepts a value..
- `'--output'`: The parser accepts a value..
- `'--mode'`: choices=MODES + ['deployed']; default='deployed'.
- `'--policy'`: choices=POLICIES.
- `'--stream'`: action='store_true'.
- `'--max-requests'`: type=int; default=64.

[s16_reader_study.py](s16_reader_study.py)

The file provides fresh validation and reserved tests for the compiled coefficient reader.

The module defines these callable interfaces:

```python

def prepare()
def arms(stage)
def trials(stage)
def freeze()
def streams()
def check_freeze()
def main()

```

The imported project modules are `s02_engine`, `s05_study`, `s14_reader`.

The command accepts these parser options:

- `'stage'`: choices=['prepare', 'validation', 'freeze', 'test', 'streams'].

## Data and supporting files

- [reader_deployment.json](reader_deployment.json): This file contains structured records from the parent calculation.

- [reader_freeze.json](reader_freeze.json): This file contains structured records from the parent calculation.

- [reader_protocol.json](reader_protocol.json): This file contains structured records from the parent calculation.

- [reader_scheduler.log](reader_scheduler.log): This file contains saved program messages.
