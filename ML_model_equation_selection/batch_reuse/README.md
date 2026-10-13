# batch reuse

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

[s00_common.py](s00_common.py)

The file provides batch equation choices for the restricted, exact vacuum coefficient system.

The module defines these callable interfaces:

```python

def sha(p)
def options(r)
def dependency(targets, permutation)
def cost(rows)
def feature(targets, p)
def predict(model, x)
def select(targets, mode, model=None)
def make_case(stage, k, r, B, n)
def symbolic_oracle(rho, b)
def substitute(p, L)
def encode(rows)
def decode(rows)
def load_model(name)

```

The imported project modules are `s00_math`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent / 'higher_loops'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model' / name.replace('.json', '.bin.gz')).read_bytes()
p.read_bytes()

```

[s01_train.py](s01_train.py)

The program trains a fast predictor of shared equation-substitution cost.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`, `sklearn`.

The imported project modules are `s00_common`.

These source constants locate inputs and outputs:

```python

B = [5, 7, 9, 11, 13, 14][k // 2 % 6]
B = [8, 12][k // 3 % 2]
B = [10, 14][k // 3 % 2]

```

This entry point uses the paths and options set in its source.

[s02_reduce.py](s02_reduce.py)

The file provides kira integration with learned batch choices and shared exact checks.

The module defines these callable interfaces:

```python

def solve(request, mode, model_name)
def apply(request, mode, model_name)
def save(path, result)
def main()

```

The imported project modules are `s00_common`, `s08_reader`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--mode'`: default='deployed'.
- `'--model'`: default='forest16.json'.

These calls show the stored input and output interface:

```python

(w / 'targets').write_text(''.join((str(len(ordered) + i) + '\n' for i in range(len(target)))))
(w / 'masters').write_text(''.join((str(i) + '\n' for i in range(r))))
(w / 'jobs.yaml').write_text(previous.JOBS)
(w / 'results/Tuserweight/kira_targets.kira').read_text()
a.input.read_text()
(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'resource_plan.json').read_text()
(OLD / 'trained_model/depth4.json').read_text()

```

[s03_study.py](s03_study.py)

The file provides sequential paired fresh-case evaluation, with all calculation costs counted.

The module defines these callable interfaces:

```python

def trial(c, mode, model, out)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'stage'`: choices=['pilot', 'validation', 'test'].

These calls show the stored input and output interface:

```python

out.read_text()
(HERE / 'trained_model/freeze.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()

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
#$ -N KiraBatch
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s07_compact.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s05_check.py
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s03_study.py "$1"

```

[s05_check.py](s05_check.py)

The file provides independent arithmetic and domain checks, including equivalent loop expansions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`, `s08_reader`, `s10_polynomial`.

This entry point uses the paths and options set in its source.

[s06_select.py](s06_select.py)

The program selects only on validation complete costs, then freeze before fresh tests.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()

```

[s07_compact.py](s07_compact.py)

The program stores exactly the same trained trees in a bounded compact representation.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model' / name.replace('.json', '.bin.gz')).write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
(HERE / 'trained_model' / name).read_text()
c.read_text()

```

[s08_reader.py](s08_reader.py)

The file provides fast exact integer-polynomial reader with the previous rational reader as fallback.

The module defines these callable interfaces:

```python

class GeneralCoefficient
def trim(p)
def add(a, b)
def mul(a, b)
def norm(p, d)
def parse(text, symbol)

```

The imported project modules are `s00_common`, `s10_polynomial`.

Import this helper module from the stage that uses it.

[s09_application.py](s09_application.py)

The file provides public entry point for the frozen, validated batch reduction deployment.

The imported project modules are `s02_reduce`.

This entry point uses the paths and options set in its source.

[s10_analyze.py](s10_analyze.py)

The file provides fresh-case complete times and independent exact audits of saved reductions.

The module defines these callable interfaces:

```python

def object_read(h)
def interval(values)
def main()

```

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'objects' / (h + '.json.gz')).read_bytes()
(HERE / 'trained_model/deployment.json').read_text()
p.read_text()
(HERE / 'model_test/test_complete.json').read_text()
(HERE / 'trained_model/freeze.json').read_text()

```

[s11_pack.py](s11_pack.py)

The program reduces several independent mass profiles in one exact Kira system.

The module defines these callable interfaces:

```python

def packed(requests, mode, model_name)
def apply(requests, mode, model)
def main()

```

The imported project modules are `s00_common`, `s08_reader`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--mode'`: default='deployed'.
- `'--model'`: default='forest16.json'.
- `'--separate'`: action='store_true'.

These calls show the stored input and output interface:

```python

(w / 'targets').write_text(''.join((str(len(ordered) + i) + '\n' for i in range(len(targets)))))
(w / 'masters').write_text(''.join((str(j) + '\n' for j in range(m))))
(w / 'jobs.yaml').write_text(driver.previous.JOBS)
(w / 'results/Tuserweight/kira_targets.kira').read_text()
a.input.read_text()
(HERE / 'trained_model/deployment.json').read_text()
(OLD / 'trained_model/depth4.json').read_text()

```

[s12_pack_study.py](s12_pack_study.py)

The file provides paired packed/separate applications, preserving identical targets and checks.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'stage'`: choices=['validation', 'test'].

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'trained_model/freeze.json').read_text()
dest.read_text()
c.read_text()

```

[s13_run.sh](s13_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraBatchNext
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s06_select.py
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s12_pack_study.py validation
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s06_select.py
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s03_study.py test
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s12_pack_study.py test
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s10_analyze.py

```

[s14_pack_analyze.py](s14_pack_analyze.py)

The program audits every saved packed result against the independent original loop oracle.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`, `s10_analyze`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment.json').read_text()
p.read_text()
(HERE / x['input']).read_text()

```

[s15_integration.py](s15_integration.py)

The program checks production entry points, extended loop values and exact fallback.

The module defines these callable interfaces:

```python

def module(name, file)
def main()

```

The imported project modules are `s00_common`, `s10_analyze`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment.json').read_text()
out.read_text()
out2.read_text()
file.read_text()

```

[s16_native.py](s16_native.py)

The program compiles unchanged trained trees and compare all scores exactly.

The module defines these callable interfaces:

```python

def load_native(name)
def select_native(targets, mode, model=None)
def compile_models()

```

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

src.write_text(source)
(HERE / 'trained_model' / name).read_text()

```

[s17_application.py](s17_application.py)

The program applies identical learned choices through a native inference library.

The module defines these callable interfaces:

```python

def module(name, file)
def main()

```

The imported project modules are `s00_common`, `s16_native`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--backend'`: choices=['native', 'python', 'control', 'deployed', 'previous']; default='deployed'.
- `'--model'`: default='forest4.json'.
- `'--separate'`: action='store_true'.

These calls show the stored input and output interface:

```python

a.input.read_text()
(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'trained_model/native_deployment.json').read_text()
obj.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))

```

[s18_native_study.py](s18_native_study.py)

The file provides fresh native-inference validation followed by frozen independent confirmation.

The module defines these callable interfaces:

```python

def records(stage)
def med(rows, backend, group)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'stage'`: choices=['prepare', 'validation', 'freeze', 'test'].

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/deployment.json').read_text()
p.read_text()
(HERE / 'trained_model/native_freeze.json').read_text()
dest.read_text()
(HERE / 'trained_model/freeze.json').read_text()

```

[s19_run.sh](s19_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraBatchNative
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 gcc/9.5.0
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s14_pack_analyze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s15_integration.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s16_native.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s18_native_study.py prepare
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s18_native_study.py validation
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s18_native_study.py freeze
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s18_native_study.py test

```

[s20_native_analyze.py](s20_native_analyze.py)

The program audits native-backend confirmation and compare full applications.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`, `s10_analyze`, `s10_polynomial`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/native_deployment.json').read_text()
p.read_text()
(HERE / x['input']).read_text()

```

[s21_plot.py](s21_plot.py)

The file provides reproducible figures of complete exact application times.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()
(HERE / 'model_test/native_summary.json').read_text()
(ROOT / 'report/figures' / p.name).write_bytes(p.read_bytes())
p.read_bytes()

```

[s22_document.py](s22_document.py)

The program writes report and READMEs from audited complete calculation results.

The module defines these callable interfaces:

```python

def read(n)
def ratio(x)
def interval(x)
def block(path, start, end, new)
def main()

```

The imported project modules are `s00_common`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(text)
(HERE / 'report_template.tex.in').read_text()
(ROOT / 'report/batch_reuse.tex').write_text(text.replace('backend', 'inference implementation'))
f.read_text()
f.write_text(text)
(HERE / 'README.md').write_text(readme)
(HERE / n).read_text()
f.write_text(text + '\n' + '\\input{batch_reuse}' + '\n')
f.write_text(text.replace('higher_loop_acceleration.tex references.bib', 'higher_loop_acceleration.tex batch_reuse.tex references.bib'))
(HERE / folder / 'README.md').write_text('# ' + folder.replace('_', ' ').capitalize() + '\n\n' + body + '\n')

```

[s23_release_check.py](s23_release_check.py)

The program releases guards for exactness, unchanged earlier studies and the storage ceiling.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/report.tex').read_text()
(HERE / 'resource_plan.json').read_text()
(HERE / name).read_text()
(HERE / 'model_test' / n).read_text()
(HERE / 'model_test/integration/summary.json').read_text()
(HERE / 'training/native_check.json').read_text()
p.read_text()
p.read_bytes()
(ROOT / 'report/references.bib').read_text()
path.read_text()

```

[s24_native_application_check.py](s24_native_application_check.py)

The program checks the final public deployment and compiled backend at extended loop orders.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_common`, `s10_analyze`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

f.read_text()
inp.read_text()
out.read_text()

```

## Data and supporting files

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

## Child folders

- [development_initial](development_initial/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
