# cumulative speedup

This folder compares three complete reductions of the restricted vacuum family.
The methods use the saved original Kira, the later full-pool control and the specialized recurrence method.
Every method receives the same targets, mass profiles and loop orders.
All 120 measured workflows pass exact checks.
The geometric mean speedup is 543.815 relative to the original control.
This result includes exact recurrence reuse and implementation changes.
It is not an isolated machine learning gain.

`s01_cases.py` defines eight groups with three mass profiles each.
Each group requests loop orders one through twelve.
`s02_worker.py` runs one complete request.
`s03_study.py` controls preparation, freezing and tests.
`s10_parallel.py` assigns matched groups to four scheduled CPU slots.

Use the scheduler wrapper with four slots and distinct cores:

```bash
qsub -pe shared 4 -binding env linear:4 Kira_comparison/cumulative_speedup/s04_run.sh pipeline
```

This command repeats a completed study.
Use it only for a deliberate new reproduction.
Keep the existing results and freeze record.
Each worker has a 2,400 MiB address-space limit and a 1,200-second limit.
Each worker has a 64 MiB scratch limit.
Complete time includes fresh-process startup, input, identities, exact algebra, checks, output writing and output reading.
Queue waiting, offline training and the later independent audit remain outside the timer.

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

[s01_cases.py](s01_cases.py)

The program declares independent matched requests without fitting any policy.

The module defines these callable interfaces:

```python

def make_group(index, maximum, count, pilot=False)
def main()

```

The imported project modules are `s00_cumulative`.

This entry point uses the paths and options set in its source.

[s02_worker.py](s02_worker.py)

The program runs a complete matched reduction and save lossless exact coefficients.

The module defines these callable interfaces:

```python

def original(requests, arm, archive_logs=False)
def main()

```

The imported project modules are `s00_cumulative`.

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

The imported project modules are `s00_cumulative`.

The command accepts these parser options:

- `'stage'`: choices=['pilot', 'freeze', 'test', 'shard'].
- `'--shard'`: type=int.

These calls show the stored input and output interface:

```python

Path('/proc/cpuinfo').read_text()

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
elif [ "$1" = "pipeline" ]; then
 "$PYTHON" "$BASE/s03_study.py" freeze
 "$PYTHON" "$BASE/s10_parallel.py"
 bash "$BASE/s09_finish.sh"
else
 "$PYTHON" "$BASE/s03_study.py" "$1"
fi

```

[s05_audit.py](s05_audit.py)

The program audits every saved coefficient, paired input system and frozen dependency.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `sympy`.

The imported project modules are `s00_cumulative`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(OBJECTS / (a['raw_export_sha256'] + '.txt.gz')).read_bytes()

```

[s06_analyze.py](s06_analyze.py)

The program reports direct cumulative ratios and absolute times on the same cases.

The module defines these callable interfaces:

```python

def compare(groups, left, right, metric)
def main()

```

The imported project modules are `s00_cumulative`.

This entry point uses the paths and options set in its source.

[s07_plot.py](s07_plot.py)

The program creates standalone scientific plots of the direct cumulative comparison.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_cumulative`.

This entry point uses the paths and options set in its source.

[s08_document.py](s08_document.py)

The program writes measured cumulative results into the scientific report and READMEs.

The module defines these callable interfaces:

```python

def replace_block(text, start, end, body)
def main()

```

The imported project modules are `s00_cumulative`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

(HERE / 'report_template.tex.in').read_text()
(ROOT / 'report/cumulative_speedup.tex').write_text(template)
p.read_text()
p.write_text(text)
citation.read_text()
citation.write_text(replace_block(bib, '% cumulative-data-begin', '% cumulative-data-end', body))

```

[s09_finish.sh](s09_finish.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCumFinish
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
PYTHON=.tools/seed-model/venv/bin/python
BASE=Kira_comparison/cumulative_speedup
"$PYTHON" "$BASE/s05_audit.py"
"$PYTHON" "$BASE/s06_analyze.py"
"$PYTHON" "$BASE/s07_plot.py"
"$PYTHON" "$BASE/s08_document.py" "$@"
make -C report

```

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

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

- [protocol.json](protocol.json): This file contains structured records from the parent calculation.

- [report_build.log](report_build.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [development](development/README.md).

- [objects](objects/README.md).

- [pilot](pilot/README.md).

- [test](test/README.md).
