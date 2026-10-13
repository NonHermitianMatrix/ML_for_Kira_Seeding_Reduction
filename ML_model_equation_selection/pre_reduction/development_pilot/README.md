# development pilot

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

[s00_contract.py](s00_contract.py)

The file provides exact polynomial pre-reduction of the restricted vacuum identities.

The module defines these callable interfaces:

```python

def module(name, path)
def normalize(a, d)
def from_fraction(p)
def fractions(p)
def subtract(a, b, delta)
def euler(a, k, rho)
def selected(request, mode, model)
def recurrence(request, rows)
def expression(p)
def allocated(p)
def guard()
def save(path, result)

```

The imported project modules are `s00_common`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BATCH = HERE.parent / 'batch_reuse'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
dest.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))

```

[s01_application.py](s01_application.py)

The program pre-reduces selected exact identities, then finish and check with Kira.

The module defines these callable interfaces:

```python

def validate_group(requests)
def calculate(requests, mode, inject_failure=False)
def apply(requests, mode, inject_failure=False)
def main()

```

The imported project modules are `s00_contract`, `s08_reader`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--mode'`: choices=['deployed', 'baseline', 'model', 'extreme', 'analytic']; default='deployed'.

These calls show the stored input and output interface:

```python

(w / 'system.kira').write_text(''.join(equations))
(w / 'targets').write_text(''.join((str(n) + '\n' for n in targets)))
(w / 'masters').write_text(''.join((str(n) + '\n' for n in range(m))))
(w / 'jobs.yaml').write_text(pack.driver.previous.JOBS)
(w / 'results/Tuserweight/kira_targets.kira').read_text()
a.input.read_text()
(HERE / 'deployment.json').read_text()

```

[s02_study.py](s02_study.py)

The file provides fresh disjoint validation and reserved comparisons of exact pre-reduction.

The module defines these callable interfaces:

```python

def records(stage)
def med(rows, method, group, key='complete_seconds')
def check_freeze()
def main()

```

The imported project modules are `s00_contract`.

The command accepts these parser options:

- `'stage'`: choices=['prepare', 'pilot', 'validation', 'freeze', 'test'].

These calls show the stored input and output interface:

```python

(HERE / 'freeze.json').read_text()
p.read_text()
out.read_text()
(BATCH / 'trained_model' / name).read_text()

```

[s03_run.sh](s03_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPreReduce
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s02_study.py prepare
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s02_study.py pilot

```

