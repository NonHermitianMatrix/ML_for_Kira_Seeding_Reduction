# development initial

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

The file provides batch equation choices for the restricted, exact vacuum coefficient system.

The module defines these callable interfaces:

```python

def sha(p)
def options(r)
def dependency(targets, permutation)
def cost(rows)
def feature(targets, p)
def predict(model, x)
def select(targets, mode, model=None)
def make_case(stage, k, r, B, n)
def symbolic_oracle(rho, b)
def substitute(p, L)
def encode(rows)
def decode(rows)

```

The imported project modules are `s00_math`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent / 'higher_loops'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

p.read_bytes()

```

[s01_train.py](s01_train.py)

The program trains a fast predictor of shared equation-substitution cost.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`, `sklearn`.

The imported project modules are `s00_common`.

These source constants locate inputs and outputs:

```python

B = [5, 7, 9, 11, 13, 14][k // 2 % 6]
B = [8, 12][k // 3 % 2]
B = [10, 14][k // 3 % 2]

```

This entry point uses the paths and options set in its source.

[s02_reduce.py](s02_reduce.py)

The file provides kira integration with learned batch choices and shared exact checks.

The module defines these callable interfaces:

```python

def solve(request, mode, model_name)
def apply(request, mode, model_name)
def save(path, result)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--mode'`: default='deployed'.
- `'--model'`: default='forest16.json'.

These calls show the stored input and output interface:

```python

(w / 'targets').write_text(''.join((str(len(ordered) + i) + '\n' for i in range(len(target)))))
(w / 'masters').write_text(''.join((str(i) + '\n' for i in range(r))))
(w / 'jobs.yaml').write_text(previous.JOBS)
(w / 'results/Tuserweight/kira_targets.kira').read_text()
a.input.read_text()
(HERE / 'trained_model' / model_name).read_text()
(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'resource_plan.json').read_text()
(OLD / 'trained_model/depth4.json').read_text()

```

[s03_study.py](s03_study.py)

The file provides sequential paired fresh-case evaluation, with all calculation costs counted.

The module defines these callable interfaces:

```python

def trial(c, mode, model, out)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'stage'`: choices=['pilot', 'validation', 'test'].

These calls show the stored input and output interface:

```python

out.read_text()
(HERE / 'trained_model/freeze.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()

```

[s04_run.sh](s04_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraBatch
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s03_study.py "$1"

```

