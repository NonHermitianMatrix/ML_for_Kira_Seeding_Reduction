# ML model equation selection

This folder contains the equation-selection model and its later extensions.
The model scores identities for the requested targets.
Exact Kira reduction checks the selected system.
The current native application is in `early_generation/`.
It makes the decision before symbolic coefficient construction.
The other child folders retain earlier methods and specialized vacuum methods.
Use each folder's guide to identify its inputs and supported physical domain.

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
(HERE / 'integration' / os.getenv('KIRA_EQ_BUILD_RECORD', 'build.json')).write_text(json.dumps(dict(sources=records, header_sha256=sha(header), binary_sha256=sha(binary), link_command=link), indent=2) + '\n')
header.read_text()
(BUILD / 'compile_commands.json').read_text()
dest.write_text(t)
(HERE / 'integration' / (name + '.patch')).write_text(''.join(difflib.unified_diff(p.read_text().splitlines(True), t.replace(str(header), header.name).splitlines(True), fromfile=str(p.relative_to(ROOT)), tofile=name)))
(ROOT / 'Kira_comparison/parallel_inference/build.json').read_text()
p.read_bytes()

```

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
def workflow(c, n, mode, threshold, out, ref, base='native', basis=None)
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
(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'trained_model/freeze.json').read_text()
pathlib.Path(os.environ['KIRA_EQ_VALIDATION_GRID']).read_text()
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
.tools/seed-model/venv/bin/python ML_model_equation_selection/s13_check_labels.py
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

[s11_reduce.py](s11_reduce.py)

The program applies the third policy with a prescribed basis; target reference coefficients are optional.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_experiment`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--masters-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--output'`: type=pathlib.Path; required=True.
- `'--base'`: choices=['native', 'seed', 'row', 'both']; default='native'.
- `'--force-model'`: action='store_true'.

These calls show the stored input and output interface:

```python

a.family_file.read_text()
a.masters_file.read_text()
(HERE / 'trained_model/deployment.json').read_text()

```

[s12_freeze.py](s12_freeze.py)

The program chooses from completed validation only, then freeze before test reductions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s10_summarize`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment.json').write_text(json.dumps(config, indent=2) + '\n')
(HERE / 'trained_model/freeze.json').write_text(json.dumps(frozen, indent=2) + '\n')
(HERE / 'validation_grid.json').read_text()
(HERE / 'integration/lazy_verification.json').read_text()
p.read_bytes()

```

[s13_check_labels.py](s13_check_labels.py)

The program repeats a native collection to check labels and features before fitting.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_experiment`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'integration/label_verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'integration/s00_equation_policy.h').read_bytes()

```

[s14_check_fast.py](s14_check_fast.py)

The program checks that shared features preserve all learned probabilities and equation masks.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_experiment`, `s09_predict`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'integration' / os.environ.get('KIRA_EQ_PARITY_REPORT', 'fast_verification.json')).write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'trained_model/model.json').read_text()

```

[s15_build_fast.sh](s15_build_fast.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqFastBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
KIRA_EQ_HEADER=s01_fast_equation_policy.h KIRA_EQ_BINARY_NAME=kira-fast KIRA_EQ_BUILD_RECORD=build_fast.json python3 ML_model_equation_selection/s00_build.py

```

[s16_validate_fast.sh](s16_validate_fast.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqFastValidation
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s06_train.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s14_check_fast.py
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-fast
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py validate
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py validation

```

[s17_audit.py](s17_audit.py)

The program compares all completed test coefficients over Q(d).

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `sympy`.

The imported project modules are `s02_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'model_test/summary.json').read_text()
(HERE / 'trained_model/freeze.json').read_text()
(ROOT / name).read_bytes()

```

[s18_additional_checks.py](s18_additional_checks.py)

The program checks composition with existing models, basis-only use, and held-out labels.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `sympy`.

The imported project modules are `s04_experiment`, `s09_predict`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/label_metrics.json').write_text(json.dumps(label_report, indent=2) + '\n')
(HERE / 'model_test/composition.json').write_text(json.dumps(dict(all_passed=True, workflows=len(composition), results=composition), indent=2) + '\n')
(HERE / 'model_test/application_verification.json').write_text(json.dumps(dict(all_passed=True, checks=len(applications), results=applications), indent=2) + '\n')
(HERE / 'trained_model/model.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()

```

[s19_test.sh](s19_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqTest
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-lazy
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s12_freeze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py test
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py model_test
.tools/seed-model/venv/bin/python ML_model_equation_selection/s17_audit.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s18_additional_checks.py

```

[s20_build_cached.sh](s20_build_cached.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqCachedBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
KIRA_EQ_HEADER=s02_cached_equation_policy.h KIRA_EQ_BINARY_NAME=kira-cached KIRA_EQ_BUILD_RECORD=build_cached.json python3 ML_model_equation_selection/s00_build.py

```

[s21_validate_cached.sh](s21_validate_cached.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqCompactValidation
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
from pathlib import Path
import sys,json
root=Path('ML_model_equation_selection')
sys.path.insert(0,str(root.resolve()))
from s10_summarize import aggregate,ratio
batches,rows=aggregate(root/'validation')
assert len(rows)==150 and all(r['success'] for r in rows)
keys=sorted({k for b in batches for k in b['methods']})
chosen=set()
for subset in [batches]+[[b for b in batches if b['topology']==t] for t in sorted({b['topology'] for b in batches})]:
 for prefix in ['learned:','distance:']:
  chosen.add(min((ratio(subset,k,'complete_seconds')['ratio'],k) for k in keys if k.startswith(prefix))[1])
grid=[['off',0]]+[[k.split(':')[0],float(k.split(':')[1])] for k in sorted(chosen)]
(root/'validation_grid.json').write_text(json.dumps(grid,indent=2)+'\n')
(root/'validation').rename(root/'validation_fast_features')
(root/'validation').mkdir()
print('Cached validation grid',grid,flush=True)
PY
export KIRA_EQ_PARITY_VERSIONS=kira-fast,kira-compact KIRA_EQ_PARITY_TAG=cached_ KIRA_EQ_PARITY_REPORT=cached_verification.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s14_check_fast.py
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-compact
export KIRA_EQ_VALIDATION_GRID=ML_model_equation_selection/validation_grid.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py validate
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py validation

```

[s22_build_compact.sh](s22_build_compact.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqCompactBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
KIRA_EQ_HEADER=s03_compact_equation_policy.h KIRA_EQ_BINARY_NAME=kira-compact KIRA_EQ_BUILD_RECORD=build_compact.json python3 ML_model_equation_selection/s00_build.py

```

[s23_plot.py](s23_plot.py)

The program plots measured complete costs, preparation work and held-out label scores.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()
(HERE / 'model_test/label_metrics.json').read_text()
(ROOT / 'report/figures' / ('equation_' + name + '.pdf')).write_bytes((out / (name + '.pdf')).read_bytes())
(out / (name + '.pdf')).read_bytes()

```

[s24_document.py](s24_document.py)

The program writes measured results and folder documentation after all checks finish.

The module defines these callable interfaces:

```python

def read(p)
def write(p, s)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

The command accepts these parser options:

- `'--data-commit'`: default='main'.

These calls show the stored input and output interface:

```python

p.write_text(s.strip() + '\n')
p.read_text()
p.write_text(text)
p.write_text(bib)
p.write_text(s)

```

[s25_build_lazy.sh](s25_build_lazy.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqLazyBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
KIRA_EQ_HEADER=s04_lazy_equation_policy.h KIRA_EQ_BINARY_NAME=kira-lazy KIRA_EQ_BUILD_RECORD=build_lazy.json python3 ML_model_equation_selection/s00_build.py

```

[s26_validate_lazy.sh](s26_validate_lazy.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqLazyValidation
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
from pathlib import Path
import json
r=Path('ML_model_equation_selection')
s=json.loads((r/'validation/summary.json').read_text())
g=json.loads((r/'validation_grid.json').read_text())
assert s['all_exact'] and s['workflows']==5*3*len(g)
(r/'validation').rename(r/'validation_compact')
(r/'validation').mkdir()
PY
export KIRA_EQ_PARITY_VERSIONS=kira-compact,kira-lazy KIRA_EQ_PARITY_TAG=lazy_ KIRA_EQ_PARITY_REPORT=lazy_verification.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s14_check_fast.py
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-lazy
export KIRA_EQ_VALIDATION_GRID=ML_model_equation_selection/validation_grid.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py validate
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py validation

```

[s27_report.sh](s27_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s23_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s24_document.py --data-commit "${1:-main}"
make -C report all

```

[s28_stratify.py](s28_stratify.py)

The program stratifies frozen test results by the topology route fixed in validation.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s10_summarize`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/topology_summary.json').write_text(json.dumps(result, indent=2) + '\n')
(ROOT / 'report/equation_selection_domain.tex').write_text(text)
p.read_text()
p.write_text(s)
(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'model_test/summary.json').read_bytes()

```

[s29_final_report.sh](s29_final_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqFinalReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s24_document.py --data-commit "${1:-main}"
.tools/seed-model/venv/bin/python ML_model_equation_selection/s23_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s28_stratify.py
make -C report all

```

[s30_confirmation.py](s30_confirmation.py)

The program confirms a restricted deployment on six fresh physical sunrise profiles.

The module defines these callable interfaces:

```python

def check_freeze()
def prepare()
def exact_record(r, ref, cache)
def confirm()

```

The imported external packages are `numpy`, `sympy`.

The imported project modules are `s02_records`, `s04_experiment`, `s10_summarize`.

These source constants locate inputs and outputs:

```python

OUT = HERE / 'model_test/confirmation'

```

The command accepts these parser options:

- `'action'`: choices=['prepare', 'confirm'].

These calls show the stored input and output interface:

```python

(HERE / 'families_confirmation.json').write_text(json.dumps(manifest, indent=2) + '\n')
(HERE / 'trained_model/deployment_confirmed.json').write_text(json.dumps(config, indent=2) + '\n')
(HERE / 'trained_model/confirmation_freeze.json').write_text(json.dumps(frozen, indent=2) + '\n')
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(OUT / 'composition_summary.json').write_text(json.dumps(composition, indent=2) + '\n')
(OUT / 'verification.json').write_text(json.dumps(audit, indent=2) + '\n')
(HERE / 'trained_model/confirmation_freeze.json').read_text()
(HERE / 'families_confirmation.json').read_text()
(HERE / 'families.json').read_text()
(ROOT / n).read_bytes()
p.read_bytes()

```

[s31_reduce.py](s31_reduce.py)

The program applies the confirmed equation policy within its measured target domain.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_experiment`.

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--masters-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--output'`: type=pathlib.Path; required=True.
- `'--base'`: choices=['native', 'seed', 'row', 'both']; default='native'.

These calls show the stored input and output interface:

```python

a.family_file.read_text()
a.masters_file.read_text()
(HERE / 'trained_model/deployment_confirmed.json').read_text()

```

[s32_confirm.sh](s32_confirm.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqConfirm
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-lazy
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s30_confirmation.py confirm

```

[s33_confirm_document.py](s33_confirm_document.py)

The program documents the restricted deployment and independent confirmation.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'model_test/confirmation'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/figures/equation_confirmed_costs.pdf').write_bytes((plot / 'confirmed_costs.pdf').read_bytes())
(ROOT / 'report/equation_selection_confirmation.tex').write_text(text)
p.read_text()
p.write_text(v)
(OUT / 'README.md').write_text(info.strip() + '\n')
(OUT / 'report_values.json').write_text(json.dumps(dict(learned=z, distance=d, composition=joint, audit=a), indent=2) + '\n')
(OUT / 'summary.json').read_text()
(OUT / 'verification.json').read_text()
(OUT / 'composition_summary.json').read_text()
(plot / 'confirmed_costs.pdf').read_bytes()
(HERE / name / 'README.md').write_text(body + '\n')
(HERE / 'trained_model/README.md').read_text()

```

[s34_confirmed_report.sh](s34_confirmed_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqConfirmedReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s24_document.py --data-commit "${1:-main}"
.tools/seed-model/venv/bin/python ML_model_equation_selection/s23_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s28_stratify.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s33_confirm_document.py
make -C report all

```

[s35_reduce.py](s35_reduce.py)

The program applies equation selection only in its measured beneficial standalone domain.

The module defines these callable interfaces:

```python

def choose(c, size, base, config)
def main()

```

The imported project modules are `s04_experiment`.

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--masters-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--output'`: type=pathlib.Path; required=True.
- `'--base'`: choices=['native', 'seed', 'row', 'both']; default='native'.

These calls show the stored input and output interface:

```python

a.family_file.read_text()
a.masters_file.read_text()
(HERE / 'trained_model/deployment_final.json').read_text()

```

[s36_check_deployment.py](s36_check_deployment.py)

The program verifies that deployment selects measured successful arms and guards combinations.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_records`, `s35_reduce`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment_verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'trained_model/deployment_final.json').read_text()
(HERE / 'families_confirmation.json').read_text()
(HERE / 'families.json').read_text()
p.read_bytes()

```

[s37_finish_documentation.py](s37_finish_documentation.py)

The program finalizes deployment documentation without changing either frozen experiment.

The module defines these callable interfaces:

```python

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

p.read_text()
p.write_text(text)
(HERE / 'README.md').write_text(readme)
(HERE / 'model_test/confirmation/summary.json').read_text()
(HERE / 'trained_model/deployment_verification.json').read_text()

```

[s38_plot.py](s38_plot.py)

The program plots measured complete costs, preparation work and held-out label scores.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()
(HERE / 'model_test/label_metrics.json').read_text()
(ROOT / 'report/figures' / ('equation_' + name + '.pdf')).write_bytes((out / (name + '.pdf')).read_bytes())
(out / (name + '.pdf')).read_bytes()

```

[s39_finish_report.sh](s39_finish_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqFinishReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s24_document.py --data-commit "${1:-main}"
.tools/seed-model/venv/bin/python ML_model_equation_selection/s38_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s28_stratify.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s33_confirm_document.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s36_check_deployment.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s37_finish_documentation.py
make -C report all

```

## Data and supporting files

- [families.json](families.json): This file defines the families in this collection.

- [families_confirmation.json](families_confirmation.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [validation_grid.json](validation_grid.json): This file contains structured records from the parent calculation.

## Child folders

- [batch_reuse](batch_reuse/README.md).

- [development_v1](development_v1/README.md).

- [development_v2](development_v2/README.md).

- [early_generation](early_generation/README.md).

- [exact_backend](exact_backend/README.md).

- [higher_loops](higher_loops/README.md).

- [integration](integration/README.md).

- [model_test](model_test/README.md).

- [polynomial_reuse](polynomial_reuse/README.md).

- [pre_reduction](pre_reduction/README.md).

- [references](references/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).

- [validation_compact](validation_compact/README.md).

- [validation_fast_features](validation_fast_features/README.md).

- [validation_full_features](validation_full_features/README.md).

## Additional scattering training

The [scattering study](scattering_training/README.md) fits and tests trees for three additional structures.
It includes rational and symbolic kinematics with separate training, validation and test batches.
Read its measured results before selecting a learned policy.

## Complete reduction cost

The [complete-cost study](../ML_model_workflow_selection/README.md)
compares models that choose a full reduction strategy from measured time.
It combines seed bounds, saved seed and equation filters, integral ordering,
and the existing temporary database change.
It also compares separate target requests with their joint reduction.
The study includes full native IBP generation and all fallback costs.
It retains the earlier model weights and results.
Its native cases cover seven graph structures at one through three loops.
The restricted vacuum results through twelve loops remain a separate result.
See that folder for the frozen model, test summaries and application commands.
