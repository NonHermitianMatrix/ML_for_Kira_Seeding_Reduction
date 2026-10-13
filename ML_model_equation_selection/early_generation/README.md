# early generation

This model selects seed--operator pairs before Kira constructs their coefficients.
It uses seventeen features that do not require symbolic equation coefficients.
The training set contains 153,124 candidate equations and 12,270 positive labels.
The labels record support in a native reference reduction.
They do not identify uniquely necessary equations.

The current application is `s12_reduce.py`.
The selected tree has depth twelve for double-box requests.
It has depth eight for the tested vacuum and ladder requests.
Both trees use threshold 0.01.
The recorded 21-target sunrise request uses the preceding equation policy.
The native route retains native seed and row choices.

The comparison completed 280 workflows on eight new parameter profiles.
The complete-time ratio to native choices is 0.942907.
The preparation-time ratio is 0.637888.
All comparisons and eight additional applications pass exact checks.
These gains apply to the tested structures and rational kinematics with symbolic dimension.

Run the application from the project root in a scheduled job:

```bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s12_reduce.py --family-file FAMILY.json --masters-file MASTERS.json --size 128 --output ML_model_equation_selection/early_generation/application/RESULT.json.gz
```

The family file follows the case format in `families_test.json`.
The master file contains the prescribed master index list.
Choose a new output file.
The application does not need reference target coefficients.
An incomplete filtered attempt repeats with native equations and then with enlarged bounds.
A coefficient mismatch is an error.

The original development order includes build, collection, training, validation, composition tests, freeze, reserved tests and analysis.
The script entries below identify each stage.
Keep completed freeze records unchanged.
Use `s04_workflows.read` to read `early-shared-v1` records and their shared objects.
The reader checks the object hashes.

Each native attempt uses one thread and a 70-second limit.
References can use 90 seconds.
The address-space limit is 2,400 MiB.
The sampled process-tree memory limit is 2,100 MiB.
The scratch limit is 16 MiB.

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
ROOT = HERE.parents[1]
BUILD = ROOT / '.tools/kira-build'
OUT = ROOT / '.tools/kira-early-generation'

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

[s01_develop.sh](s01_develop.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyDevelop
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
python3 ML_model_equation_selection/early_generation/s00_build.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s04_workflows.py collect
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s02_train.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s04_workflows.py pilot

```

[s02_train.py](s02_train.py)

The program fits a small target-dependent CART probability model using training groups only.

The module defines these callable interfaces:

```python

def train(name, depth, minchild)

```

The imported external packages are `numpy`.

The imported project modules are `s02_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(dest / 'model.json').write_text(json.dumps(model, indent=2) + '\n')
(dest / 'weights.txt').write_text(str(len(nodes)) + '\n' + ''.join((f"{z['feature']} {z['threshold']:.17g} {z['left']} {z['right']} {z['probability']:.17g}\n" for z in nodes)))
(HERE / 'training' / (name + '_summary.json')).write_text(json.dumps({k: v for k, v in model.items() if k not in ('nodes', 'features')}, indent=2) + '\n')
pathlib.Path(__file__).read_bytes()
p.read_bytes()

```

[s03_early_run.py](s03_early_run.py)

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

MODEL_HOME = pathlib.Path(__file__).resolve().parent.parent
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

[s04_workflows.py](s04_workflows.py)

The file provides bounded native comparisons for decisions made before equation construction.

The module defines these callable interfaces:

```python

def canonical(value)
def payload(name)
def read(p)
def sha(p)
def setup()
def guard()
def save(p, r)
def cases(split, additional_only=False)
def set_policy(binary, mode, threshold=0, model=None)
def reference(c, n)
def workflow(c, n, label, ref, out, binary=EARLY, mode='off', threshold=0, model=None, basis=None, base='native', weights=None, started=None)
def collect()
def pilot()

```

The imported project modules are `s02_records`, `s03_early_run`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
PARENT = HERE.parent
ROOT = HERE.parents[1]
OLD = '.tools/kira-equation-selection/kira-lazy'
EARLY = '.tools/kira-early-generation/kira'

```

The command accepts these parser options:

- `'action'`: choices=['collect', 'pilot'].

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
(HERE / 'additional_families.json').read_text()
pathlib.Path(p).read_bytes()
(PARENT / 'families.json').read_text()

```

[s05_develop_fresh.sh](s05_develop_fresh.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyDevelop
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s04_workflows.py collect
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s02_train.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s04_workflows.py pilot

```

[s06_validate.py](s06_validate.py)

The program compares complete costs and choose validation candidates without reading reserved results.

The module defines these callable interfaces:

```python

def rows(directory)
def aggregate(rs)
def gmean(xs)
def compare(bs, label, base='early_off')
def controls()
def candidates()
def method(label)
def confirm()
def summarize()

```

The imported project modules are `s04_workflows`.

The command accepts these parser options:

- `'action'`: choices=['controls', 'candidates', 'confirm', 'summarize'].

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(dict(by_topology=selected, batches=bs), indent=2) + '\n')
(HERE / 'validation/summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(HERE / 'validation/candidates.json').read_text()

```

[s07_validate.sh](s07_validate.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyValidate
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s08_parity.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s06_validate.py controls
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s06_validate.py candidates
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s06_validate.py confirm
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s06_validate.py summarize

```

[s08_parity.py](s08_parity.py)

The program checks the compiled early gate against saved Python probabilities on training candidates.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s04_workflows`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'validation/prediction_parity.json').write_text(json.dumps(result, indent=2) + '\n')
context.write_text(f"{len(c['definition']['loop_momenta'])} {len(c['definition']['external_momenta'])} {r['size']} {len(r['targets'][0])}\n" + '\n'.join((' '.join(map(str, t)) for t in r['targets'])) + '\n')
f.read_text()
(HERE / 'trained_model' / name / 'model.json').read_text()

```

[s09_compact.py](s09_compact.py)

The program stores repeated exact outputs once, verifying lossless record recovery.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_workflows`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'validation/storage_integrity.json').write_text(json.dumps(audit, indent=2) + '\n')
p.read_bytes()

```

[s10_composition.py](s10_composition.py)

The program validates early equation filtering together with the existing trained row policy.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_workflows`, `s06_validate`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'validation/composition_summary.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'validation/summary.json').read_text()
(ROOT / 'Kira_comparison/integrated_runtime/deployment.json').read_text()

```

[s11_composition.sh](s11_composition.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyCompose
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s09_compact.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s10_composition.py

```

[s12_reduce.py](s12_reduce.py)

The program runs the frozen early equation policy with exact native fallback.

The module defines these callable interfaces:

```python

def structural_key(c)
def previous(c, n)
def select(c, n, policy)
def reduce(c, n, out, reference=None, basis=None, policy='deployed', started=None)
def main()

```

The imported project modules are `s04_workflows`, `s06_validate`.

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--masters-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--output'`: type=pathlib.Path; required=True.
- `'--policy'`: choices=['deployed', 'native', 'previous']; default='deployed'.

These calls show the stored input and output interface:

```python

(PARENT / 'trained_model/deployment_final.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()
a.family_file.read_text()
a.masters_file.read_text()

```

[s13_freeze.py](s13_freeze.py)

The program freezes the validated policies, integration and reserved protocol before tests.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s04_workflows`, `s06_validate`, `s108_reduce`, `s12_reduce`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment.json').write_text(json.dumps(config, indent=2) + '\n')
(HERE / 'families_test.json').write_text(json.dumps(manifest, indent=2) + '\n')
dest.write_text(json.dumps(frozen, indent=2) + '\n')
(HERE / 'validation/final_selection.json').read_text()
(HERE / 'validation/prediction_parity.json').read_text()
(HERE / 'split_audit.json').read_text()
(HERE / 'validation/candidates.json').read_text()
(HERE / 'families_test.json').read_text()
(ROOT / 'Kira_comparison/integrated_runtime/deployment.json').read_text()
(HERE / 'trained_model' / m / 'model.json').read_text()
p.read_bytes()

```

[s14_test.py](s14_test.py)

The program evaluates the frozen policy on previously reserved physical profiles.

The module defines these callable interfaces:

```python

def check()
def exact(r, ref, seen)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s04_workflows`, `s12_reduce`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/verification.json').write_text(json.dumps(audit, indent=2) + '\n')
(HERE / 'trained_model/freeze.json').read_text()
(HERE / 'families_test.json').read_text()

```

[s15_test.sh](s15_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyTest
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s16_seed_composition.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s13_freeze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s14_test.py

.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s18_analyze.py

```

[s16_seed_composition.py](s16_seed_composition.py)

The program measures the existing seed model with early filtering before release selection.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_workflows`, `s06_validate`, `s108_reduce`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'validation/final_selection.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'validation/summary.json').read_text()
(HERE / 'validation/composition_summary.json').read_text()

```

[s17_seed_composition.sh](s17_seed_composition.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlySeed
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s16_seed_composition.py

```

[s18_analyze.py](s18_analyze.py)

The program summarizes fixed-test timings with physical-profile resampling.

The module defines these callable interfaces:

```python

def comparison(bs, method, base)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s04_workflows`, `s06_validate`, `s14_test`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(HERE / 'model_test/verification.json').read_text()
(HERE / 'trained_model' / name / 'model.json').read_text()

```

[s19_plot.py](s19_plot.py)

The program draws comparisons from the frozen, independently checked test results.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

The imported project modules are `s04_workflows`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()

```

[s20_check_release.py](s20_check_release.py)

The program verifies deployment routing and preserve the preceding frozen releases.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s04_workflows`, `s12_reduce`, `s14_test`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment_verification.json').write_text(json.dumps(audit, indent=2) + '\n')
(HERE / 'model_test/summary.json').read_text()
(HERE / 'families_test.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()
p.read_text()
p.read_bytes()

```

[s21_document.py](s21_document.py)

The program writes the report and release summaries from audited fixed-test results.

The module defines these callable interfaces:

```python

def block(path, start, end, text, prepend=False)
def main()

```

The imported project modules are `s04_workflows`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(s)
path.write_text(path.read_text().replace('selecting IBP seeds and allowed elimination steps', 'selecting IBP seeds, equations and allowed elimination steps'))
(HERE / 'report_template.tex.in').read_text()
(report / 'equation_selection_early.tex').write_text(template.replace('@@RESULTS@@', results).replace('@@AUDIT@@', audit).replace('¤', '$'))
path.write_text(t)
path.write_text(path.read_text().replace('equation_selection_confirmation.tex references.bib', 'equation_selection_confirmation.tex equation_selection_early.tex references.bib'))
(HERE / 'model_test/summary.json').read_text()
(HERE / 'model_test/verification.json').read_text()
(HERE / 'trained_model/deployment_verification.json').read_text()

```

[s22_finish.sh](s22_finish.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyFinish
#$ -l h_rt=00:15:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s18_analyze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s19_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s20_check_release.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s21_document.py "$@"

```

## Data and supporting files

- [additional_families.json](additional_families.json): This file contains structured records from the parent calculation.

- [families_test.json](families_test.json): This file contains structured records from the parent calculation.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [reserved_parameters.json](reserved_parameters.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [split_audit.json](split_audit.json): This file records checks of the corresponding calculation.

## Child folders

- [bottleneck_audit](bottleneck_audit/README.md).

- [development_overlap](development_overlap/README.md).

- [integration](integration/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [references](references/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
