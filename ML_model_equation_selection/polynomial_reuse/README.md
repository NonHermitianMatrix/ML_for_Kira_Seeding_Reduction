# polynomial reuse

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

[s00_arithmetic.py](s00_arithmetic.py)

The file provides shared exact Taylor terms and integer loop-order transformations.

The module defines these callable interfaces:

```python

def normalized(values, denominator)
def multiply(left, right, limit)
class TaylorCheck
class Transforms
def expand(rows, loops, transforms)
def allocated(path)
def guard()
def object_store(value)
def save(path, result)

```

The imported project modules are `s00_contract`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRE = HERE.parent / 'pre_reduction'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
p.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))

```

[s01_engine.py](s01_engine.py)

The program preserves exact reduction and verification while reusing arithmetic work.

The module defines these callable interfaces:

```python

class State
def calculate(requests, variant, policy, state, inject_failure=False)
def apply(requests, variant='both', policy='extreme', state=None, inject_failure=False)

```

The imported project modules are `s00_arithmetic`, `s16_native`.

Import this helper module from the stage that uses it.

[s02_application.py](s02_application.py)

The file provides single-request and bounded persistent-worker interfaces.

The module defines these callable interfaces:

```python

def process(command, variant, policy, state)
def main()

```

The imported project modules are `s01_engine`.

The command accepts these parser options:

- `'--input'`: type=Path.
- `'--output'`: type=Path.
- `'--variant'`: choices=['deployed', 'baseline', 'transforms', 'taylor', 'both']; default='deployed'.
- `'--policy'`: choices=['extreme', 'model']; default='extreme'.
- `'--stream'`: action='store_true'.
- `'--max-requests'`: type=int; default=64.

These calls show the stored input and output interface:

```python

inp.read_text()
(HERE / 'deployment.json').read_text()

```

[s03_check.py](s03_check.py)

The file provides independent arithmetic and persistent-interface checks.

The module defines these callable interfaces:

```python

def kernel()
def integration()

```

The imported project modules are `s01_engine`.

The command accepts these parser options:

- `'stage'`: choices=['kernel', 'integration'].

These calls show the stored input and output interface:

```python

(folder / ('output' + str(i) + '.json')).read_text()
(HERE / 'objects' / (x['coefficients_sha256'] + '.json.gz')).read_bytes()

```

[s04_study.py](s04_study.py)

The file provides fresh validation and reserved single-request and stream comparisons.

The module defines these callable interfaces:

```python

def read_rows(stage)
def median(rows, group, variant, key='complete_seconds')
def check_freeze()
def prepare()
def freeze()
def trials(stage)
def streams()
def main()

```

The imported project modules are `s00_arithmetic`.

The command accepts these parser options:

- `'stage'`: choices=['prepare', 'validation', 'freeze', 'test', 'streams'].

These calls show the stored input and output interface:

```python

p.read_text()
dest.read_text()
(HERE / 'deployment.json').read_text()
(HERE / n).read_text()
(HERE / 'model_test/results' / (groups[j].stem + '_baseline_0.json')).read_text()
filename.read_text()

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
#$ -N KiraPolyStudy
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s03_check.py kernel
.tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s04_study.py prepare
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/polynomial_reuse/s04_study.py validation
.tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s04_study.py freeze
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/polynomial_reuse/s04_study.py test
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/polynomial_reuse/s04_study.py streams
.tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s03_check.py integration

```

[s06_audit.py](s06_audit.py)

The program audits stored exact results against the older loop-dependent formula.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/integration/summary.json').read_text()
p.read_text()
inp.read_text()
(HERE / 'objects' / (h + '.json.gz')).read_bytes()

```

[s07_analyze.py](s07_analyze.py)

The program separates arithmetic and process-reuse effects in the complete measurements.

The module defines these callable interfaces:

```python

def ratio(rows, num, den, key)
def main()

```

The imported project modules are `s04_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/audit.json').read_text()
(HERE / 'deployment.json').read_text()
p.read_text()
(HERE / g).read_text()

```

[s08_plot.py](s08_plot.py)

The program exports standalone figures for exact arithmetic and persistent processing.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_arithmetic`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()

```

[s09_document.py](s09_document.py)

The program updates the report and READMEs from frozen arithmetic-reuse measurements.

The module defines these callable interfaces:

```python

def block(path, key, text)
def main()

```

The imported project modules are `s00_arithmetic`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(old)
(HERE / 'report_template.tex.in').read_text()
(ROOT / 'report/polynomial_reuse.tex').write_text(text)
p.read_text()
p.write_text(old)
(HERE / 'model_test/summary.json').read_text()
p.write_text(old + '\n' + '\\input{polynomial_reuse}' + '\n')
p.write_text(old.replace('pre_reduction.tex references.bib', 'pre_reduction.tex polynomial_reuse.tex references.bib'))
(p / 'README.md').write_text(description + '\n')

```

[s10_release_check.py](s10_release_check.py)

The program checks frozen methods, exact evidence, report references and resource bounds.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s04_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/report.tex').read_text()
(HERE / 'model_test/audit.json').read_text()
(HERE / 'model_test/summary.json').read_text()
(HERE / 'resource_plan.json').read_text()
(ROOT / 'report/polynomial_reuse.tex').read_text()
(HERE / 'model_test/integration/summary.json').read_text()
(HERE / 'validation/kernel_check.json').read_text()
p.read_text()
(ROOT / 'report/references.bib').read_text()
(HERE.parent / folder / 'trained_model/freeze.json').read_text()
p.read_bytes()

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
#$ -N KiraPolyReport
#$ -l h_rt=00:20:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s09_document.py "$@"
.tools/seed-model/venv/bin/python ML_model_equation_selection/polynomial_reuse/s10_release_check.py
make -C report all

```

## Data and supporting files

- [audit_scheduler.log](audit_scheduler.log): This file records checks of the corresponding calculation.

- [deployment.json](deployment.json): This file contains structured records from the parent calculation.

- [final_report_scheduler.log](final_report_scheduler.log): This file contains saved program messages.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [report_scheduler.log](report_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [validation](validation/README.md).
