# Kira comparison

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

[s00_prepare.py](s00_prepare.py)

The program freezes outcome-independent held-out cases, models, and resource limits.

The module defines these callable interfaces:

```python

def sha(p)
def key(s)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'ML_model_seed_selection/split_manifest.json').read_text()
out.write_text(json.dumps(plan, indent=2) + '\n')
p.read_bytes()
out.read_text()

```

[s01_common.py](s01_common.py)

The file provides public inputs and exact coefficient arithmetic for paired Kira comparisons.

The module defines these callable interfaces:

```python

def read(p)
def write(p, v)
def sha(p)
def load_module(name, path)
def ranking(s)
def load_case(case, size)
def connected(eqs, targets, masters)
def rational_rows(terms)
def expression_terms(row)
def exact_check(rows, family)
def sample_point(definition)

```

The imported external packages are `sympy`.

The imported project modules are `s02_common`, `s03_kira_adapter`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / 'integrals'
SUFF = ROOT / 'ML_model_seed_selection/kira_sufficiency_test'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

t.write_text(json.dumps(v, indent=2, allow_nan=False) + '\n')
pathlib.Path(p).read_text()

```

[s02_worker.py](s02_worker.py)

The file provides one isolated symbolic reduction, with live inference and exact fallback.

The module defines these callable interfaces:

```python

def kira_run(w, plan)
def supplied(family, targets, selected, w, plan)
def seed_select(fam)
def reduce_targets(fam, learned=True)
def native(fam, trim, w, plan)
def main()

```

The imported external packages are `sympy`, `torch`.

The imported project modules are `s01_common`, `s01_state`, `s05_predict`, `s08_verify`, `s17_native_combine`.

The command accepts these parser options:

- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')
torch.load(ROOT / 'ML_model_seed_selection/trained_model.pt', map_location='cpu', weights_only=False)
(w / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(w / 'config/kinematics.yaml').write_text(json.dumps(kin))
(w / 'targets').write_text(''.join((label(a) + '\n' for a in component)))
(w / 'masters').write_text(''.join((label(a) + '\n' for a in fam['masters'])))
(w / 'jobs.yaml').write_text(json.dumps({'jobs': [{'reduce_sectors': reduction}, {'kira2file': {'target': [['targets']]}}]}))

```

[s03_run.py](s03_run.py)

The program runs counterbalanced matched trials with bounded processes and archived evidence.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def allocated(p)
def rss_tree(pid)
def limits()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

The command accepts these parser options:

- `'--pilot'`: action='store_true'.
- `'--case'`: type=int.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
p.read_text()
p.read_text(errors='replace')
pathlib.Path('/proc/%d/task/%d/children' % (p, p)).read_text()
pathlib.Path('/proc/%d/statm' % p).read_text()
pathlib.Path('/proc/cpuinfo').read_text()

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
#$ -N KiraCost
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COMPARISON_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-cost-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_COMPARISON_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/s03_run.py "$@"

```

[s05_array.sh](s05_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostFull
#$ -t 1-19
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/results
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COMPARISON_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-cost-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_COMPARISON_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/s03_run.py --case "$((SGE_TASK_ID-1))"

```

[s06_freeze_inputs.py](s06_freeze_inputs.py)

The program records and enforce the exact inputs and executable sources before repeated tests.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s07_audit.py](s07_audit.py)

The program checks final exports, selected identities, paths and complete trial coverage.

The module defines these callable interfaces:

```python

def vector(terms, point, p)
def main()

```

The imported project modules are `s01_common`, `s08_verify`.

This entry point uses the paths and options set in its source.

[s08_summarize.py](s08_summarize.py)

The program summarizes matched repetitions, resource outcomes and distinct cost measures.

The module defines these callable interfaces:

```python

def median(v)
def mean(v)
def geo(v)
def counter(r, key)
def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s09_plot.py](s09_plot.py)

The program plots verified matched runtime, solver work, model work and memory.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s10_native_worker.py](s10_native_worker.py)

The file provides native Kira seeding from frozen learned seed envelopes, with default fallback.

The module defines these callable interfaces:

```python

def native_selected(fam, trim, w, plan, selected, margin=1)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s01_common`, `s02_worker`, `s17_native_combine`.

The command accepts these parser options:

- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(w / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(w / 'config/kinematics.yaml').write_text(json.dumps(kin))
(w / 'targets').write_text(''.join((label(a) + '\n' for a in component)))
(w / 'masters').write_text(''.join((label(a) + '\n' for a in fam['masters'])))
(w / 'jobs.yaml').write_text(json.dumps({'jobs': [{'reduce_sectors': reduction}, {'kira2file': {'target': [['targets']]}}]}))
logpath.read_text(errors='replace')

```

[s11_native_run.py](s11_native_run.py)

The program runs counterbalanced matched trials with bounded processes and archived evidence.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def allocated(p)
def rss_tree(pid)
def limits()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

The command accepts these parser options:

- `'--pilot'`: action='store_true'.
- `'--case'`: type=int.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
p.read_text()
p.read_text(errors='replace')
pathlib.Path('/proc/%d/task/%d/children' % (p, p)).read_text()
pathlib.Path('/proc/%d/statm' % p).read_text()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s12_native_array.sh](s12_native_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraNativeSeeds
#$ -t 1-7
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/native_seed/results
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COMPARISON_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-cost-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_COMPARISON_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/s11_native_run.py --case "$((SGE_TASK_ID-1))"

```

[s13_native_audit.py](s13_native_audit.py)

The program checks final exports, selected identities, paths and complete trial coverage.

The module defines these callable interfaces:

```python

def vector(terms, point, p)
def main()

```

The imported project modules are `s01_common`, `s08_verify`.

These source constants locate inputs and outputs:

```python

HERE = HERE / 'native_seed'

```

This entry point uses the paths and options set in its source.

[s14_prepare_native.py](s14_prepare_native.py)

The program freezes the native seed-envelope comparison on the same seven independent bases.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s15_native_summary.py](s15_native_summary.py)

The program summarizes matched repetitions, resource outcomes and distinct cost measures.

The module defines these callable interfaces:

```python

def median(v)
def mean(v)
def geo(v)
def counter(r, key)
def main()

```

The imported project modules are `s01_common`.

These source constants locate inputs and outputs:

```python

HERE = HERE / 'native_seed'

```

This entry point uses the paths and options set in its source.

[s16_native_plot.py](s16_native_plot.py)

The program plots the direct native seed-envelope comparison.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s17_native_combine.py](s17_native_combine.py)

The program combines native component reductions with exact Fermat algebra through Kira.

The module defines these callable interfaces:

```python

def combine(family, path, work, plan, solver)

```

The imported project modules are `s01_common`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

path.read_text()

```

[s18_native_regression.py](s18_native_regression.py)

The program checks the previously slow native combination and the learned native envelope.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s03_run`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

f.read_text(errors='replace')

```

[s19_regression.sh](s19_regression.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCombineCheck
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/native_regression.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COMPARISON_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-cost-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_COMPARISON_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/s18_native_regression.py "$@"

```

[s20_finalize.sh](s20_finalize.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostAudit
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/finalization.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 32768
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/s07_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/s08_summarize.py
.tools/seed-model/venv/bin/python Kira_comparison/s09_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/s13_native_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/s15_native_summary.py
.tools/seed-model/venv/bin/python Kira_comparison/s16_native_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/s23_cost_breakdown.py
python - <<'PY'
import json,pathlib
p=pathlib.Path('.tools/kira-comparison-publication/completion.json');x=json.loads(p.read_text());x['stage']='comparisons_validated';p.write_text(json.dumps(x,indent=2)+'\n')
print('Both comparisons validated and plotted')
PY

```

[s21_update_report.py](s21_update_report.py)

The program writes the checked comparison into the paper and preserve the supplied abstract.

The module defines these callable interfaces:

```python

def comparison(data, baseline, policy)
def ratio_fields(c)
def figure(name, caption, label)
def replace_once(text, old, new)
def main()

```

The imported project modules are `s01_common`.

The command accepts these parser options:

- `'data_commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

(report / 'kira_comparison.tex').write_text(content, encoding='utf-8')
p.read_text(encoding='utf-8')
p.write_text(text, encoding='utf-8')
p.read_text()
p.write_text(t)
p.write_text(t, encoding='utf-8')
backup.write_text(text, encoding='utf-8')

```

[s22_readmes.py](s22_readmes.py)

The program documents the validated comparison without changing models or integral data.

The module defines these callable interfaces:

```python

def append(path, marker, paragraph)
def get(data, baseline, policy)
def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

path.write_text(text + '\n' + marker + '\n' + paragraph + '\n', encoding='utf-8')
path.read_text(encoding='utf-8')

```

[s23_cost_breakdown.py](s23_cost_breakdown.py)

The program separates measured stages and family outcomes after exact validation.

The module defines these callable interfaces:

```python

def med(v)
def geo(v)
def summarize(folder)
def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s24_resume_native.py](s24_resume_native.py)

The program resumes native cases after enlarging only the retained-evidence storage guard.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--case'`: type=int; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'native_seed/storage_guard_extension.json').read_text()

```

[s25_resume_array.sh](s25_resume_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraNativeResume
#$ -t 1-7
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/native_seed/results
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COMPARISON_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-cost-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_COMPARISON_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/s24_resume_native.py --case "$((SGE_TASK_ID-1))"

```

[s26_resume_audit.py](s26_resume_audit.py)

The program checks the storage-only resumption and preservation of fixed mathematical inputs.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s27_finish_resumed.sh](s27_finish_resumed.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraNativeAudit
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/resumed_finalization.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 32768
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/s13_native_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/s26_resume_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/s15_native_summary.py
.tools/seed-model/venv/bin/python Kira_comparison/s16_native_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/s23_cost_breakdown.py
python - <<'PY'
import json,pathlib
p=pathlib.Path(".tools/kira-comparison-publication/completion.json")
x=json.loads(p.read_text());x["stage"]="comparisons_validated";p.write_text(json.dumps(x,indent=2)+"\n")
print("Both comparisons validated and plotted; storage-only resumption checked.")
PY

```

## Data and supporting files

- [cost_breakdown.json](cost_breakdown.json): This file contains structured records from the parent calculation.

- [finalization.log](finalization.log): This file contains saved program messages.

- [frozen_inputs.json](frozen_inputs.json): This file contains structured records from the parent calculation.

- [native_regression.log](native_regression.log): This file contains saved program messages.

- [plan.json](plan.json): This file contains structured records from the parent calculation.

- [resumed_finalization.log](resumed_finalization.log): This file contains saved program messages.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [acceleration](acceleration/README.md).

- [adapter_v2_partial](adapter_v2_partial/README.md).

- [cumulative_speedup](cumulative_speedup/README.md).

- [fast_expression](fast_expression/README.md).

- [figures](figures/README.md).

- [generalization](generalization/README.md).

- [integrated_runtime](integrated_runtime/README.md).

- [live_matrix](live_matrix/README.md).

- [multiloop_native](multiloop_native/README.md).

- [native_regression](native_regression/README.md).

- [native_seed](native_seed/README.md).

- [native_seed_preflight](native_seed_preflight/README.md).

- [native_seed_three_method_preflight](native_seed_three_method_preflight/README.md).

- [parallel_inference](parallel_inference/README.md).

- [pilot](pilot/README.md).

- [pilot_adapter_v1](pilot_adapter_v1/README.md).

- [results](results/README.md).
