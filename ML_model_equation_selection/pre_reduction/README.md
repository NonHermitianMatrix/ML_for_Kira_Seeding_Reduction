# pre reduction

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

The imported project modules are `s00_common`, `s16_native`.

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

The imported project modules are `s00_contract`, `s08_reader`, `s16_native`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--mode'`: choices=['deployed', 'baseline', 'model', 'extreme', 'analytic', 'direct_model', 'direct_extreme', 'direct_analytic']; default='deployed'.

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

[s04_check.py](s04_check.py)

The file provides independent arithmetic, application, fallback and final-output checks.

The module defines these callable interfaces:

```python

def kernel()
def integration()
def audit()
def main()

```

The imported project modules are `s00_contract`, `s01_application`, `s02_study`, `s08_reader`, `s10_polynomial`.

The command accepts these parser options:

- `'stage'`: choices=['kernel', 'integration', 'audit'].

These calls show the stored input and output interface:

```python

p.read_text()
(HERE / 'objects' / (record['payload_sha256'] + '.json.gz')).read_bytes()
(HERE / record['input']).read_text()

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
#$ -N KiraPreFull
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s04_check.py kernel
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s02_study.py validation
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s02_study.py freeze
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s02_study.py test
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s04_check.py integration
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s04_check.py audit

```

[s06_analyze.py](s06_analyze.py)

The file provides matched complete-time ratios and exactness summaries.

The module defines these callable interfaces:

```python

def compare(rows, num, den, key)
def main()

```

The imported project modules are `s00_contract`, `s02_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/audit.json').read_text()
p.read_text()
(HERE / 'deployment.json').read_text()
(HERE / g).read_text()

```

[s07_plot.py](s07_plot.py)

The file provides standalone plots from matched independent measurements.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_contract`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()

```

[s08_document.py](s08_document.py)

The program updates scientific text and READMEs from checked measurements.

The module defines these callable interfaces:

```python

def block(path, key, text)
def main()

```

The imported project modules are `s00_contract`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(old)
(HERE / 'report_template.tex.in').read_text()
(ROOT / 'report/pre_reduction.tex').write_text(text)
p.read_text()
p.write_text(old)
(HERE / 'model_test/summary.json').read_text()
p.write_text(old + '\n' + '\\input{pre_reduction}' + '\n')
p.write_text(old.replace('batch_reuse.tex references.bib', 'batch_reuse.tex pre_reduction.tex references.bib'))
(HERE / folder / 'README.md').write_text(description + '\n')

```

[s09_release_check.py](s09_release_check.py)

The program verifies frozen code, exact evidence, report references and resource bounds.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_contract`, `s02_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/report.tex').read_text()
(HERE / 'resource_plan.json').read_text()
(HERE / 'model_test/summary.json').read_text()
(HERE / 'model_test/integration/summary.json').read_text()
p.read_text()
(ROOT / 'report/references.bib').read_text()
(HERE / 'model_test/audit.json').read_text()
p.read_bytes()

```

[s10_report.sh](s10_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPreReport
#$ -l h_rt=00:20:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s12_check_deployed.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s06_analyze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s07_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s08_document.py "$@"
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s09_release_check.py
make -C report all

```

[s11_resume.sh](s11_resume.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPreFull
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s02_study.py test
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s04_check.py integration
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s04_check.py audit
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s06_analyze.py

```

[s12_check_deployed.py](s12_check_deployed.py)

The program verifies the public deployed interface and its exact expanded output.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_contract`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

out.read_text()
(HERE / 'objects' / (x['payload_sha256'] + '.json.gz')).read_bytes()
p.read_text()
(HERE / 'deployment.json').read_text()

```

## Data and supporting files

- [deployment.json](deployment.json): This file contains structured records from the parent calculation.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [resume_scheduler.log](resume_scheduler.log): This file contains saved program messages.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [development_pilot](development_pilot/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [pilot](pilot/README.md).

- [validation](validation/README.md).
