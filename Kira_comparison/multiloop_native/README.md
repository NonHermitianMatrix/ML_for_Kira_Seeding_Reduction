# multiloop native

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

[s00_storage.sh](s00_storage.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraStorage
#$ -l h_rt=00:20:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C
python - <<'PY'
import json,subprocess,time
from pathlib import Path
p=Path('Kira_comparison/multiloop_native/storage_audit.json')
begin=time.time()
r=subprocess.run(['du','-s','-B1','.'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=1000)
out=dict(elapsed_seconds=time.time()-begin,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr[-3000:],local_observed_bytes=262680576,local_allowance_bytes=400000000)
if r.returncode==0:out['cluster_allocated_bytes']=int(r.stdout.split()[0])
p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
PY

```

[s01_families.py](s01_families.py)

The program defines native integral families and independent targets before experiments.

The module defines these callable interfaces:

```python

def definition(kind, parameters)
def targets(d)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(plan, indent=2) + '\n')
p.read_bytes()

```

[s02_run.py](s02_run.py)

The program runs one bounded complete Kira reduction, retaining compact exact evidence.

The module defines these callable interfaces:

```python

def sha(p)
def label(a)
def limits()
def disk(path)
def process_rss(pid)
def parse_export(text)
def run(case, size, policy, output, timeout=300, margin=1, reference=None, weights=None, records=True, archive=True, check_masters=False, force=None, scratch_cap=None)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s04_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
(scratch / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(scratch / 'config/kinematics.yaml').write_text(json.dumps(dict(kinematics=kin)))
(scratch / 'targets').write_text(''.join((label(a) + '\n' for a in target)))
(scratch / 'jobs.yaml').write_text(json.dumps(jobs))
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s03_pilot.sh](s03_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostPilot
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_00_sunrise --policy stock --output Kira_comparison/multiloop_native/pilot_v3/sunrise_stock.json.gz
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_00_sunrise --policy collect --reference Kira_comparison/multiloop_native/pilot_v3/sunrise_stock.json.gz --output Kira_comparison/multiloop_native/pilot_v3/sunrise_collect.json.gz
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_02_double_box --policy stock --output Kira_comparison/multiloop_native/pilot_v3/box_stock.json.gz
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_04_vacuum3 --policy stock --output Kira_comparison/multiloop_native/pilot_v3/vacuum_stock.json.gz

```

[s04_records.py](s04_records.py)

The program shares scientific evidence with atomic writes and a storage bound.

The module defines these callable interfaces:

```python

def payload(value)
def retained()
def put(path, data)
def write_record(path, record)
def read_record(path)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()

```

[s05_development.py](s05_development.py)

The program collects cost labels only from the fixed training and validation cases.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_run`, `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'case'`: type=int.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s06_development.sh](s06_development.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostData
#$ -l h_rt=00:25:00,h_data=3G,h_vmem=4G
#$ -t 1-9
#$ -tc 3
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s05_development.py "$((SGE_TASK_ID-1))"

```

[s07_seed.py](s07_seed.py)

The program applies the saved seed model to a finite native Laporta seed region.

The module defines these callable interfaces:

```python

def distribute(total, n)
def _candidates(n, physical, r, s, d)
def candidates(definition, r, s, d)
def choose(definition, masters, targets, spec, closure=False, use_model=True, threshold=0.01)

```

The imported external packages are `numpy`.

The imported project modules are `s21_seed_loader`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

[s08_workflow.py](s08_workflow.py)

The program completes native workflows with bounded fallback and exact reference checks.

The module defines these callable interfaces:

```python

def execute(case, size, policy, output, reference, timeout=360, weights=None, trace=False, start=None)

```

The imported project modules are `s02_run`, `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

reference.read_bytes()
weights.read_bytes()

```

[s09_validate.py](s09_validate.py)

The program measures closed-loop validation costs before reserving final test results.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_run`, `s04_records`, `s08_workflow`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: type=int.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s10_validate.sh](s10_validate.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostValid
#$ -l h_rt=03:30:00,h_data=3G,h_vmem=4G
#$ -t 1-3
#$ -tc 3
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s09_validate.py "$((SGE_TASK_ID-1))"

```

[s11_rollouts.py](s11_rollouts.py)

The program measures downstream algebraic work after one alternative native source choice.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s02_run`, `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s12_rollouts.sh](s12_rollouts.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostRoll
#$ -l h_rt=01:30:00,h_data=3G,h_vmem=4G
#$ -t 1-9
#$ -tc 2
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s11_rollouts.py "$((SGE_TASK_ID-1))"

```

[s13_audit_families.py](s13_audit_families.py)

The program checks that denominators span the independent loop scalar products.

The module defines these callable interfaces:

```python

def audit()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(dict(cases=results, all_passed=True), indent=2) + '\n')
(HERE / 'families.json').read_text()

```

[s14_worker.py](s14_worker.py)

The file provides one fresh measured workflow process; evidence writing follows the stop time.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s08_workflow`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'output'`: type=pathlib.Path.
- `'reference'`: type=pathlib.Path.
- `'--timeout'`: type=float; default=360.
- `'--trace'`: action='store_true'.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s15_fresh.py](s15_fresh.py)

The program bounds the complete process, including model loading and exact verification.

The module defines these callable interfaces:

```python

def descendants(pid)
def limits()
def execute_fresh(case, size, policy, output, reference, timeout=360, trace=False)

```

The imported project modules are `s02_run`, `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(t / 'children').read_text()

```

[s16_validate_fresh.py](s16_validate_fresh.py)

The program compares frozen candidate workflows in fresh validation processes.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s02_run`, `s04_records`, `s15_fresh`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE.parents[1] / 'ML_model_reduction/cost_training/trained_model.json').read_text()
(HERE / 'runtime_check.json').read_text()
(HERE / 'families.json').read_text()

```

[s17_validate_fresh.sh](s17_validate_fresh.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostFresh
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -t 1-3
#$ -tc 3
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s16_validate_fresh.py "$((SGE_TASK_ID-1))"

```

[s18_freeze.py](s18_freeze.py)

The program selects seed settings on validation and freeze all final scientific inputs.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

out.write_text(json.dumps(record, indent=2) + '\n')
(HERE / 'runtime_check.json').read_text()
p.read_bytes()
(model / 'trained_model.json').read_text()

```

[s19_reserved.py](s19_reserved.py)

The program runs the fixed, independent native multiloop comparison.

The module defines these callable interfaces:

```python

def reference_run(*args, **kwargs)
def main(index)

```

The imported project modules are `s02_run`, `s04_records`, `s15_fresh`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
(HERE / 'freeze.json').read_text()
(HERE / 'families.json').read_text()
(ROOT / name).read_bytes()

```

[s20_reserved.sh](s20_reserved.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostTest
#$ -l h_rt=06:00:00,h_data=3G,h_vmem=4G
#$ -t 1-6
#$ -tc 3
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s19_reserved.py "$((SGE_TASK_ID-1))"

```

[s21_seed_loader.py](s21_seed_loader.py)

The program loads unchanged NumPy weights with one filesystem read per archive.

The module defines these callable interfaces:

```python

class NativeSeed

```

The imported external packages are `numpy`.

The imported project modules are `s01_fast_seed`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(EXPORT / 'seed_export.json').read_bytes()
(EXPORT / 'seed_weights.npz').read_bytes()

```

[s22_install_runtime.py](s22_install_runtime.py)

The program installs bounded per-workflow seed caches after the earlier validation jobs end.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(t)

```

[s23_prepare.sh](s23_prepare.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostReady
#$ -l h_rt=00:15:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s12_promote_tree.py
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s22_install_runtime.py
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s24_check_runtime.py

```

[s24_check_runtime.py](s24_check_runtime.py)

The program checks unchanged seed probabilities and C++/Python tree decisions.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s01_fast_seed`, `s02_run`, `s04_records`, `s07_seed`, `s08_train_tree`, `s21_seed_loader`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'runtime_check.json').write_text(json.dumps(result, indent=2) + '\n')
(ROOT / 'ML_model_reduction/cost_training/trained_model.json').read_text()
(HERE / 'families.json').read_text()

```

[s25_analyze.py](s25_analyze.py)

The program summarizes every reserved outcome and form paired descriptive comparisons.

The module defines these callable interfaces:

```python

def median(a)
def comparison(records, left, right, size=None, metric='complete_seconds')
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(HERE / 'freeze.json').read_text()
interruption.read_text()
path.read_bytes()

```

[s26_verify.py](s26_verify.py)

The program parses exported reductions and verify exact rational coefficients.

The module defines these callable interfaces:

```python

def rational(text)
def parse(record)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'freeze.json').read_text()
(HERE / 'baseline_diagnostic/summary.json').read_text()
(ROOT / 'ML_model_reduction/cost_training/trained_model.json').read_text()
(HERE / 'summary.json').read_text()
(HERE / 'runtime_check.json').read_text()
(ROOT / name).read_bytes()
(HERE / name).read_bytes()

```

[s27_analyze.sh](s27_analyze.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostAudit
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s25_analyze.py
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s26_verify.py

```

[s28_freeze.sh](s28_freeze.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostFreeze
#$ -l h_rt=00:05:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s18_freeze.py

```

[s29_plot.py](s29_plot.py)

The program plots complete times, algebraic counts and completion including fallback.

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

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').read_text()
(HERE / 'freeze.json').read_text()
(HERE / 'families.json').read_text()

```

[s30_plot.sh](s30_plot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostPlots
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s29_plot.py

```

[s31_document.py](s31_document.py)

The program writes result prose and numeric provenance from checked, frozen comparisons.

The module defines these callable interfaces:

```python

def load(name)
def num(v)
def ratio(c)
def main()
def write_readmes(s, v, f)
def write_conclusion(s, f)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_multiloop_results.tex').write_text(text)
(HERE / 'report_values.json').write_text(json.dumps(values, indent=2) + '\n')
p.read_text()
p.write_text(text)
p.write_text(text.rstrip() + '\n\n' + marker + '\n## Reserved outcomes\n\n' + block + '\n' + end + '\n')
p.write_text(old)
(HERE / name).read_text()
p.write_text(s0)
(HERE / 'summary.json').read_bytes()
(HERE / 'verification.json').read_bytes()
(HERE / 'freeze.json').read_bytes()
(HERE / 'baseline_diagnostic/summary.json').read_bytes()

```

[s32_build_report.sh](s32_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostReport
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
export LC_ALL=C LANG=C OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
make -C report

```

[s33_baseline_diagnostic.py](s33_baseline_diagnostic.py)

The file provides post-comparison diagnostic of stock and instrumented smaller-region failures.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_run`, `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(out / 'summary.json').write_text(json.dumps(record, indent=2) + '\n')
(HERE / 'families.json').read_text()

```

[s34_baseline_diagnostic.sh](s34_baseline_diagnostic.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostDiag
#$ -l h_rt=00:15:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s33_baseline_diagnostic.py

```

## Data and supporting files

- [concurrency_amendment.json](concurrency_amendment.json): This file contains structured records from the parent calculation.

- [families.json](families.json): This file defines the families in this collection.

- [family_audit.json](family_audit.json): This file records checks of the corresponding calculation.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [reference_resource_amendment.json](reference_resource_amendment.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [runtime_check.json](runtime_check.json): This file records checks of the corresponding calculation.

- [scheduler_interruption.json](scheduler_interruption.json): This file contains structured records from the parent calculation.

- [storage_audit.json](storage_audit.json): This file records checks of the corresponding calculation.

- [storage_rebase.json](storage_rebase.json): This file contains structured records from the parent calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [trials.csv](trials.csv): This file supports the calculation described in the parent guide.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [baseline_diagnostic](baseline_diagnostic/README.md).

- [model_test](model_test/README.md).

- [pilot](pilot/README.md).

- [pilot_v2](pilot_v2/README.md).

- [pilot_v3](pilot_v3/README.md).

- [reference_checks](reference_checks/README.md).

- [references](references/README.md).

- [reserved_references](reserved_references/README.md).

- [rollouts](rollouts/README.md).

- [runtime_checks](runtime_checks/README.md).

- [shared](shared/README.md).

- [training](training/README.md).

- [validation_final](validation_final/README.md).

- [validation_row](validation_row/README.md).

- [validation_seed](validation_seed/README.md).

- [validation_seed_safe](validation_seed_safe/README.md).
