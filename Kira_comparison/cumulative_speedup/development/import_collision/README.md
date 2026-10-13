# import collision

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

[s00_common.py](s00_common.py)

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

[s01_cases.py](s01_cases.py)

The program declares independent matched requests without fitting any policy.

The module defines these callable interfaces:

```python

def make_group(index, maximum, count, pilot=False)
def main()

```

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

[s02_worker.py](s02_worker.py)

The program runs a complete matched reduction and save lossless exact coefficients.

The module defines these callable interfaces:

```python

def original(requests, arm, archive_logs=False)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--arm'`: choices=ARMS; required=True.
- `'--archive-logs'`: action='store_true'.

[s03_study.py](s03_study.py)

The program executes paired frozen comparisons with resource monitoring.

The module defines these callable interfaces:

```python

def trial(inp, arm, rep, folder)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'stage'`: choices=['pilot', 'freeze', 'test'].

[s04_run.sh](s04_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCumulative
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
PYTHON=.tools/seed-model/venv/bin/python
BASE=Kira_comparison/cumulative_speedup
if [ "$1" = "prepare" ]; then
 "$PYTHON" "$BASE/s01_cases.py"
 "$PYTHON" "$BASE/s03_study.py" pilot
else
 "$PYTHON" "$BASE/s03_study.py" "$1"
fi

```

## Data and supporting files

- [scheduler.log](scheduler.log): This file contains saved program messages.
