# live matrix

This folder supports the calculation described in the parent guide.

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

[s00_policy_server.py](s00_policy_server.py)

The program scores admissible live Kira row operations with the frozen reduction model.

The module defines these callable interfaces:

```python

def emit(x)
def evaluate(text)
def readrow(n)
def sampled(terms)

```

The imported external packages are `torch`.

The imported project modules are `s01_state`, `s05_predict`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

[s01_live_policy.h](s01_live_policy.h)

The file provides live symbolic forward-elimination experiment; GPL-3.0-or-later.

The required headers are `chrono`, `cstdio`, `cstdlib`, `fstream`, `map`, `memory`, `algorithm`, `set`, `stdexcept`, `vector`, `spawn.h`, `sys/wait.h`, `unistd.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s02_build.py](s02_build.py)

The program builds one changed translation unit; reuse the unchanged installed Kira objects.

The module defines these callable interfaces:

```python

def sha(p)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

original.read_text()
modified.write_text(text)
(HERE / 'build.json').write_text(json.dumps(record, indent=2) + '\n')
p.read_bytes()

```

[s03_build.sh](s03_build.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/live_matrix/build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
python3 Kira_comparison/live_matrix/s02_build.py

```

[s04_worker.py](s04_worker.py)

The program runs native equation generation and choose live forward operations inside Kira.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s02_worker`, `s10_native_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = HERE.parent

```

The command accepts these parser options:

- `'case'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')
(w / 'forward.jsonl').read_text()

```

[s05_run.py](s05_run.py)

The file provides counterbalanced trials with hard time, memory, scratch and output bounds.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--case'`: type=int; required=True.
- `'--pilot'`: action='store_true'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
path.read_text(errors='replace')
(HERE / 'plan.json').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s06_run.sh](s06_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveMatrix
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/live_matrix
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_LIVE_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-live-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_LIVE_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s05_run.py "$@"

```

[s07_audit.py](s07_audit.py)

The program replays exact-operation records and verify archived native reductions.

The module defines these callable interfaces:

```python

def vec(row, point, p)
def trace_rows(text)
def check_update(src, dst, after, samples)
def main()

```

The imported project modules are `s01_common`, `s08_verify`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

[s08_summarize.py](s08_summarize.py)

The program summarizes complete paired trials and preserve incomplete-case counts.

The module defines these callable interfaces:

```python

def median(v)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s09_array.sh](s09_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveFull
#$ -t 1-7
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/live_matrix
exec bash Kira_comparison/live_matrix/s06_run.sh --case "$((SGE_TASK_ID-1))"

```

[s10_prepare.py](s10_prepare.py)

The program freezes the benchmark inputs after exact pilot checks, before repeated trials.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s07_audit`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'frozen_inputs.json').write_text(json.dumps(dict(sha256=current, model_retrained=False), indent=2) + '\n')
p.read_text()
p.read_bytes()

```

[s11_plot.py](s11_plot.py)

The program plots matched elapsed times and exact coefficient-operation counts.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

[s12_finalize.sh](s12_finalize.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveAudit
#$ -l h_rt=00:45:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/live_matrix/audit.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s07_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s08_summarize.py
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s11_plot.py

```

[s13_update_report.py](s13_update_report.py)

The program writes the measured live-matrix section and synchronize its scientific scope.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = ROOT / 'report'

```

The command accepts these parser options:

- `'data_commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

(REPORT / 'kira_live_matrix.tex').write_text(fill(section), encoding='utf-8')
p.read_text(encoding='utf-8')
p.write_text(text, encoding='utf-8')
p.read_text()
p.write_text(t)
(HERE / 'report_values.json').write_text(json.dumps(vals, indent=2) + '\n')

```

[s14_readmes.py](s14_readmes.py)

The program documents the checked live policy, controls, limits, execution and measured results.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'README.md').write_text(text)
p.read_text()
p.write_text(t + b)

```

[s15_build_report.sh](s15_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveReport
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o .tools/kira-live-publication/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s13_update_report.py "$1"
make -C report

```

## Data and supporting files

- [COPYING](COPYING): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.1](KiraLiveFull.o15109182.1): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.2](KiraLiveFull.o15109182.2): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.3](KiraLiveFull.o15109182.3): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.4](KiraLiveFull.o15109182.4): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.5](KiraLiveFull.o15109182.5): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.6](KiraLiveFull.o15109182.6): This file supports the calculation described in the parent guide.

- [KiraLiveFull.o15109182.7](KiraLiveFull.o15109182.7): This file supports the calculation described in the parent guide.

- [KiraLiveMatrix.o15108816](KiraLiveMatrix.o15108816): This file supports the calculation described in the parent guide.

- [KiraLiveMatrix.o15108848](KiraLiveMatrix.o15108848): This file supports the calculation described in the parent guide.

- [KiraLiveMatrix.o15108899](KiraLiveMatrix.o15108899): This file supports the calculation described in the parent guide.

- [KiraLiveMatrix.o15108900](KiraLiveMatrix.o15108900): This file supports the calculation described in the parent guide.

- [audit.log](audit.log): This file records checks of the corresponding calculation.

- [build.json](build.json): This file contains structured records from the parent calculation.

- [build.log](build.log): This file contains saved program messages.

- [figure_values.csv](figure_values.csv): This file supports the calculation described in the parent guide.

- [frozen_inputs.json](frozen_inputs.json): This file contains structured records from the parent calculation.

- [pilot_validation.json](pilot_validation.json): This file contains structured records from the parent calculation.

- [plan.json](plan.json): This file contains structured records from the parent calculation.

- [plot.log](plot.log): This file contains saved program messages.

- [plot_review.log](plot_review.log): This file contains saved program messages.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [figures](figures/README.md).

- [pilot](pilot/README.md).

- [results](results/README.md).
