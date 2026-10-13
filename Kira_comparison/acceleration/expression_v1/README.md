# expression v1

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

[s65_expression_worker.py](s65_expression_worker.py)

The program applies fast seed inference directly to complete stored target expressions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `name`: type=int if name in ('case', 'size') else pathlib.Path if name in ('scratch', 'output') else str.

