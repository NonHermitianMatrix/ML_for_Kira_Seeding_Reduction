# generalization

This folder tests new scattering structures and symbolic invariants.
It contains a massless nonplanar two-loop box, a massless pentagon and a box with external virtuality.
Seven batches contain 88 targets.
All seventy measured workflows pass exact checks.
All thirty-five filtered workflows require native fallback.
The complete-time ratio to native choices is 1.251829.
The application therefore defaults to native choices for these inputs.

`cases.json` defines the denominators, scalar products and targets.
`scattering_families/` contains rational parameter profiles.
`symbolic_kinematics/` contains independent symbolic invariants.
`optimal_paths/` contains finite minimum-operation checks for a bubble and a tadpole.
Each minimum applies to a stated source pool and operation cost.

Use `s12_reduce.py` for the application with a supplied basis.
Use `s02_study.py` for the recorded preparation and comparison stages.
The job wrappers supply the resource limits.
The application needs no reference target coefficients.
The mathematical checks and the timing tests use separate output files.

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

[s00_native_run.py](s00_native_run.py)

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

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL_HOME = ROOT / 'ML_model_equation_selection'
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

[s01_cases.py](s01_cases.py)

The program defines new physical scattering families without using learned scores.

The module defines these callable interfaces:

```python

def build(kind, symbolic, profile=0)
def targets(d)
def audit(d)
def case(kind, symbolic, profile, split, size)
def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'cases.json').write_text(json.dumps(manifest, indent=2) + '\n')
(HERE / directory / 'families.json').write_text(json.dumps(subset, indent=2) + '\n')

```

[s02_study.py](s02_study.py)

The file provides frozen transfer tests with symbolic coefficients and exact native fallback.

The module defines these callable interfaces:

```python

def sha(p)
def load(p)
def save(p, r)
def setup(mode='off')
def attempt(c, mode='off', ref=None, margin=0)
def reference(c)
def workflow(c, method, ref)
def freeze()
def main()

```

The imported project modules are `s00_native_run`, `s01_cases`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WEIGHTS = ROOT / 'ML_model_equation_selection/early_generation/trained_model/early_d12/weights.txt'
BINARY = ROOT / '.tools/kira-early-generation/kira'

```

The command accepts these parser options:

- `'action'`: choices=['prepare', 'pilot', 'freeze', 'test'].

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(record, indent=2) + '\n')
(HERE / 'cases.json').read_text()
p.read_bytes()
p.read_text()

```

[s03_job.sh](s03_job.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGeneral
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/generalization/s02_study.py "$@"

```

[s04_optimal_paths.py](s04_optimal_paths.py)

The program certifies minimum counted field operations over every admissible finite pivot path.

The module defines these callable interfaces:

```python

def systems()
def certificate(system)
def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'optimal_paths/summary.json').write_text(json.dumps(summaries, indent=2) + '\n')
pathlib.Path(__file__).read_bytes()

```

[s05_verify_certificates.py](s05_verify_certificates.py)

The program checks every certificate edge independently using exact symbolic matrices.

The module defines these callable interfaces:

```python

def verify(p)
def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'optimal_paths/verification.json').write_text(json.dumps(dict(success=True, systems=results), indent=2) + '\n')

```

[s06_pipeline.sh](s06_pipeline.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGeneral
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=.tools/seed-model/venv/bin/python
D=Kira_comparison/generalization
$P $D/s02_study.py test
$P $D/s04_optimal_paths.py
$P $D/s05_verify_certificates.py

```

[s07_audit.py](s07_audit.py)

The program audits symbolic exports and test a larger seed region and fresh specializations.

The module defines these callable interfaces:

```python

def expr(s)
def equal(a, b)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s00_native_run`, `s02_study`, `s04_optimal_paths`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'cases.json').read_text()

```

[s08_analyze.py](s08_analyze.py)

The program summarizes complete times without selecting a new policy from the test.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s02_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(HERE / 'cases.json').read_text()
(HERE / 'application/verification.json').read_text()
(HERE / 'verification.json').read_text()
(HERE / 'optimal_paths/verification.json').read_text()

```

[s09_audit_job.sh](s09_audit_job.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGenAudit
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/generalization/s07_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/generalization/s08_analyze.py

```

[s10_document.py](s10_document.py)

The program writes checked results and pin the report to the published data.

The module defines these callable interfaces:

```python

def replace_block(p, tag, text)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(old)
(HERE / 'README.md').write_text(readme)
rules.read_text()
(ROOT / 'report/generalization.tex').write_text(text)
p.write_text(text)
(HERE / 'summary.json').read_text()
(HERE / 'optimal_paths/summary.json').read_text()
rules.write_text(text)
(HERE / 'report_template.tex.in').read_text()

```

[s11_finish.sh](s11_finish.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGenFinish
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=.tools/seed-model/venv/bin/python
D=Kira_comparison/generalization
$P $D/s04_optimal_paths.py
$P $D/s05_verify_certificates.py
$P $D/s08_analyze.py

```

[s12_reduce.py](s12_reduce.py)

The program reduces symbolic scattering targets using a supplied basis, without target answers.

The module defines these callable interfaces:

```python

def reduce(case, masters, experimental_filter=False)
def main()

```

The imported project modules are `s00_native_run`, `s02_study`.

The command accepts these parser options:

- `'--case'`: The parser accepts a value..
- `'--family-file'`: type=pathlib.Path.
- `'--masters-file'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.
- `'--experimental-filter'`: action='store_true'.

These calls show the stored input and output interface:

```python

a.masters_file.read_text()
a.family_file.read_text()
(HERE / 'cases.json').read_text()

```

[s13_application_check.py](s13_application_check.py)

The program checks the answer-free native application and its explicit experimental fallback.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_study`, `s07_audit`, `s12_reduce`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(directory / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
p.write_text(json.dumps(frozen, indent=2) + '\n')
(location / (c['id'] + '.json')).write_text(json.dumps({'masters': ref['masters']}, indent=2) + '\n')
(HERE / 'cases.json').read_text()
p.read_text()
(HERE / 's12_reduce.py').read_bytes()

```

[s14_application_job.sh](s14_application_job.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGenApp
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/generalization/s13_application_check.py
.tools/seed-model/venv/bin/python Kira_comparison/generalization/s08_analyze.py
.tools/seed-model/venv/bin/python Kira_comparison/generalization/s10_document.py

```

## Data and supporting files

- [cases.json](cases.json): This file defines the physical cases and requested targets.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [runner_provenance.json](runner_provenance.json): This file contains structured records from the parent calculation.

- [storage_audit.json](storage_audit.json): This file records checks of the corresponding calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [application](application/README.md).

- [development](development/README.md).

- [logs](logs/README.md).

- [model_test](model_test/README.md).

- [optimal_paths](optimal_paths/README.md).

- [references](references/README.md).

- [scattering_families](scattering_families/README.md).

- [symbolic_kinematics](symbolic_kinematics/README.md).
