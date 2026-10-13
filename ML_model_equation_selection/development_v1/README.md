# development v1

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

[s00_build.py](s00_build.py)

The program compiles equation filtering and collection without changing prior binaries.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = ROOT / '.tools/kira-build'
OUT = ROOT / '.tools/kira-equation-selection'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
(HERE / 'integration/build.json').write_text(json.dumps(dict(sources=records, header_sha256=sha(header), binary_sha256=sha(OUT / 'kira'), link_command=link), indent=2) + '\n')
(BUILD / 'compile_commands.json').read_text()
dest.write_text(t)
(HERE / 'integration' / (name + '.patch')).write_text(''.join(difflib.unified_diff(p.read_text().splitlines(True), t.replace(str(header), header.name).splitlines(True), fromfile=str(p.relative_to(ROOT)), tofile=name)))
(ROOT / 'Kira_comparison/parallel_inference/build.json').read_text()
p.read_bytes()

```

[s00_equation_policy.h](s00_equation_policy.h)

The file provides learned equation filter. Exact IBP construction and algebra stay in Kira.

The required headers are `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `set`, `sstream`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s01_build.sh](s01_build.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
python3 ML_model_equation_selection/s00_build.py

```

[s02_records.py](s02_records.py)

The file provides bounded compressed exact evidence.

The module defines these callable interfaces:

```python

def read(path)
def packed(path, record)

```

The imported project modules are `s105_parallel_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

path.write_bytes(data)
(HERE / 'resource_plan.json').read_text()

```

[s03_run.py](s03_run.py)

The program runs one bounded complete Kira reduction, retaining compact exact evidence.

The module defines these callable interfaces:

```python

def sha(p)
def label(a)
def limits()
def disk(path)
def process_rss(pid)
def parse_export(text)
def run(case, size, policy, output, timeout=300, margin=1, reference=None, weights=None, records=True, archive=True, check_masters=False, force=None, scratch_cap=None, compact=True, ordering=None, basis=None)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s02_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

MODEL_HOME = pathlib.Path(__file__).resolve().parent
HERE = ROOT / 'Kira_comparison/integrated_runtime'
MODEL = ROOT / 'ML_model_reduction/cost_training'

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; default=8.
- `'--policy'`: default='stock'.
- `'--timeout'`: type=int; default=300.
- `'--margin'`: type=int; default=1.
- `'--output'`: type=pathlib.Path; required=True.
- `'--reference'`: type=pathlib.Path.
- `'--weights'`: type=pathlib.Path.
- `'--no-records'`: action='store_true'.
- `'--legacy-backsub'`: action='store_true'.
- `'--check-masters'`: action='store_true'.
- `'--ordering'`: type=int.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
(scratch / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(scratch / 'config/kinematics.yaml').write_text(json.dumps(dict(kinematics=kin)))
(scratch / 'targets').write_text(''.join((label(a) + '\n' for a in target)))
(scratch / 'jobs.yaml').write_text(json.dumps(jobs))
(scratch / 'equation_context.txt').write_text(f"{len(definition['loop_momenta'])} {len(ext)} {len(target)} {n}\n" + '\n'.join((' '.join(map(str, a)) for a in target)) + '\n')
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'equations.tsv').read_text()
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'equation_metrics.json').read_text()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s04_experiment.py](s04_experiment.py)

The program collects native labels and compare frozen filters with exact fallback.

The module defines these callable interfaces:

```python

def setup()
def cases(phase)
def reference(c, n)
def workflow(c, n, mode, threshold, out, ref, base='native')
def main()

```

The imported project modules are `s02_records`, `s03_run`, `s108_reduce`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RUNTIME = ROOT / 'Kira_comparison/integrated_runtime'

```

The command accepts these parser options:

- `'action'`: choices=['collect', 'validate', 'test', 'pilot'].

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'trained_model/freeze.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()
(ROOT / name).read_bytes()

```

[s05_run.sh](s05_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqExperiment
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py "$1"

```

[s06_train.py](s06_train.py)

The program fits a small target-dependent CART probability model using training groups only.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s02_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/model.json').write_text(json.dumps(model, indent=2) + '\n')
(HERE / 'trained_model/weights.txt').write_text(str(len(nodes)) + '\n' + ''.join((f"{z['feature']} {z['threshold']:.17g} {z['left']} {z['right']} {z['probability']:.17g}\n" for z in nodes)))
(HERE / 'training/summary.json').write_text(json.dumps({k: v for k, v in model.items() if k not in ('nodes', 'features')}, indent=2) + '\n')
pathlib.Path(__file__).read_bytes()
p.read_bytes()

```

[s07_train.sh](s07_train.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqTrain
#$ -l h_rt=00:45:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1800000
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s06_train.py

```

[s08_develop.sh](s08_develop.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqDevelop
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
 .tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py collect
.tools/seed-model/venv/bin/python ML_model_equation_selection/s06_train.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py validate

```

[s09_predict.py](s09_predict.py)

The program predicts reference-membership probabilities from the documented 24 features.

The module defines these callable interfaces:

```python

def predict(features, model)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'features'`: type=pathlib.Path.
- `'--threshold'`: type=float; default=0.01.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/model.json').read_text()
a.features.read_text()

```

[s10_summarize.py](s10_summarize.py)

The program summarizes paired timings without dropping failed filtered attempts.

The module defines these callable interfaces:

```python

def stage(r)
def aggregate(folder)
def ratio(batches, key, field)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s02_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

The command accepts these parser options:

- `'phase'`: choices=['validation', 'model_test'].

These calls show the stored input and output interface:

```python

(HERE / a.phase / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')

```

## Data and supporting files

- [build.json](build.json): This file contains structured records from the parent calculation.

- [status.json](status.json): This file records the execution state.

## Child folders

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
