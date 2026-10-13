# monitor race

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

[s00_cumulative.py](s00_cumulative.py)

The file provides shared paths, frozen provenance, bounded resources and coefficient output.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def sha(p)
def digest(x)
def allocated(p)
def guard()
def check_freeze()
def frozen_files()
def packed(rows)
def limits()
def process_ids(pid)
def stop_tree(pid)

```

The imported project modules are `s00_backend`, `s02_engine`, `s14_reader`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXACT = ROOT / 'ML_model_equation_selection/exact_backend'
HIGH = ROOT / 'ML_model_equation_selection/higher_loops'
OBJECTS = HERE / 'objects'
BINARIES = {'original_kira': ROOT / '.tools/kira/bin/kira', 'chain_baseline': ROOT / '.tools/kira-early-generation/kira'}

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

Path(p).read_text()
Path(p).read_bytes()
(t / 'children').read_text()

```

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

## Data and supporting files

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.
