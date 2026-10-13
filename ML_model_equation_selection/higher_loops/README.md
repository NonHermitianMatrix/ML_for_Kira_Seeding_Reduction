# higher loops

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

[s00_math.py](s00_math.py)

The file provides exact restricted vacuum identities and coefficient-free dependency choices.

The module defines these callable interfaces:

```python

def compositions(n, r)
def children(b, pair)
def pairs(b)
def features(b, p)
def teacher(b)
def score(nodes, x)
def choose(b, mode, nodes=None)
def closure(targets, mode, nodes=None)
def dense(r, maximum)
def validate(request)
def equation(b, p, rho, L=None)
def poly_substitute(p, L)
def rational_polynomial(s, symbol)
def canonical(p)
def oracle(L, rho, b)
def write(path, x)

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

t.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n')

```

[s01_train.py](s01_train.py)

The program trains small equation-choice trees from exact dependency counts.

The module defines these callable interfaces:

```python

def fit(x, y, depth, minchild=4)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s00_math`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

Path(__file__).read_bytes()

```

[s02_reduce.py](s02_reduce.py)

The program generates a sufficient equation system, run bounded Kira and check exact coefficients.

The module defines these callable interfaces:

```python

def sha(p)
def allocated(path)
def rss(pid)
def limits()
def run_kira(w)
def parse(text)
def export(request, mode, nodes, w, L=None)
def solve(request, mode, model=None, L=None)
def apply(request, mode='learned', model='depth8.json', shared=True)
def compact_save(path, result)
def main()

```

The imported project modules are `s00_math`, `s10_polynomial`.

These source constants locate inputs and outputs:

```python

BINARY = ROOT / '.tools/kira-early-generation/kira'
FERMAT = ROOT / '.tools/Ferl7/fer64'

```

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--mode'`: choices=['dense', 'first', 'smallest', 'largest', 'extreme', 'learned']; default='learned'.
- `'--model'`: default='depth8.json'.
- `'--separate-loops'`: action='store_true'.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')
(w / 'targets').write_text(''.join((str(len(ordered) + n) + '\n' for n in range(len(targets)))))
(w / 'masters').write_text(''.join((str(i) + '\n' for i in range(r))))
(w / 'jobs.yaml').write_text(JOBS)
(w / 'results/Tuserweight/kira_targets.kira').read_text()
a.input.read_text()
p.read_bytes()
(HERE / 'resource_plan.json').read_text()
(base / 'status').read_text()
(HERE / 'trained_model' / model).read_text()
(t / 'children').read_text()

```

[s03_cases.py](s03_cases.py)

The program creates distinct mass profiles and exponent batches before fitting or timing.

The module defines these callable interfaces:

```python

def cases(split)
def main()

```

The imported project modules are `s00_math`.

This entry point uses the paths and options set in its source.

[s04_study.py](s04_study.py)

The program runs predeclared comparisons in sequential bounded worker processes.

The module defines these callable interfaces:

```python

def trial(c, mode, model, shared, out)
def main()

```

The imported project modules are `s00_math`.

The command accepts these parser options:

- `'stage'`: choices=['pilot', 'validation', 'test'].

These calls show the stored input and output interface:

```python

out.read_text()
(HERE / 'trained_model/freeze.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()
(ROOT / n).read_bytes()

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
#$ -N KiraHigher
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/higher_loops/s04_study.py "$1"

```

[s06_select.py](s06_select.py)

The program chooses policies on validation measurements and freeze before reserved tests.

The module defines these callable interfaces:

```python

def key(r)
def main()

```

The imported project modules are `s00_math`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
p.read_bytes()

```

[s07_analyze.py](s07_analyze.py)

The program audits exact test exports and summarize the frozen paired costs.

The module defines these callable interfaces:

```python

def method(r)
def ratio(values)
def main()

```

The imported project modules are `s00_math`, `s02_reduce`, `s10_polynomial`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/freeze.json').read_text()
p.read_text()
p.read_bytes()
(ROOT / n).read_bytes()

```

[s08_application.py](s08_application.py)

The program applies the frozen higher-loop deployment to a new supported family request.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_math`, `s02_reduce`.

The command accepts these parser options:

- `'--input'`: type=Path; required=True.
- `'--output'`: type=Path; required=True.
- `'--policy'`: choices=['deployed', 'learned', 'dense']; default='deployed'.

These calls show the stored input and output interface:

```python

args.input.read_text()
(HERE / 'trained_model/deployment.json').read_text()

```

[s09_plot.py](s09_plot.py)

The program makes standalone figures from the frozen higher-loop cost audit.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_math`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'model_test/summary.json').read_text()

```

[s10_polynomial.py](s10_polynomial.py)

The file provides bounded exact reading of Kira's univariate rational coefficients.

The module defines these callable interfaces:

```python

def trim(a)
def add(a, b)
def mul(a, b)
def norm(a, b)
def ratadd(x, y)
def ratmul(x, y)
def ratpow(x, n)
def parse(s, symbol)

```

Import this helper module from the stage that uses it.

[s11_reader_audit.py](s11_reader_audit.py)

The program cross-checks a fast exact coefficient reader against symbolic algebra.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_math`, `s10_polynomial`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_bytes()
(HERE / 's10_polynomial.py').read_bytes()

```

[s12_document.py](s12_document.py)

The program documents only verified higher-loop measurements and the selected deployment.

The module defines these callable interfaces:

```python

def block(p, start, end, text, prepend=False)
def polish(t)
def main()

```

The imported project modules are `s00_math`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(s)
p.write_text(t)
(HERE / 'report_template.tex.in').read_text()
(report / 'higher_loop_acceleration.tex').write_text(polish(template))
p.write_text(p.read_text().replace('equation_selection_early.tex references.bib', 'equation_selection_early.tex higher_loop_acceleration.tex references.bib'))
(HERE / 'model_test/summary.json').read_text()
(HERE / 'model_test/verification.json').read_text()
(HERE / 'trained_model/deployment.json').read_text()
(HERE / 'trained_model' / policy['model']).read_text()
(HERE / 'validation/reader_audit.json').read_text()
(HERE / name).write_text(text)

```

[s13_release_check.py](s13_release_check.py)

The program checks release integrity, existing-data applications and storage bounds.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_math`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/freeze.json').read_text()
(HERE / 'model_test/verification.json').read_text()
old.read_text()
(HERE / 'resource_plan.json').read_text()
(HERE / 'training/examples.json.gz').read_bytes()
p.read_text()
(ROOT / n).read_bytes()

```

[s14_extrapolate.py](s14_extrapolate.py)

The program checks the frozen application at additional loop orders above the timing set.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_math`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model/freeze.json').read_text()
p.read_text()
dest.read_text()
(ROOT / n).read_bytes()

```

[s16_export_existing.py](s16_export_existing.py)

The program prepares scalar-component requests from the existing coupled vacuum dataset.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_math`.

The command accepts these parser options:

- `'family'`: The parser accepts a value..
- `'--output'`: type=Path; required=True.
- `'--target-records'`: type=int; default=8.
- `'--loops'`: type=int; nargs='+'.

These calls show the stored input and output interface:

```python

p.read_text()
source.read_bytes()

```

## Data and supporting files

- [design.json](design.json): This file contains structured records from the parent calculation.

- [pipeline_scheduler.log](pipeline_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

## Child folders

- [development_initial](development_initial/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
