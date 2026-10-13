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

[s00_exact.py](s00_exact.py)

The file provides exact Laurent polynomials in d and m2, and an independent partial-fraction oracle.

The module defines these callable interfaces:

```python

def clean(a)
def add(a, b)
def scale(a, s)
def mul(a, b)
def div(a, b)
def expr(a)
def ev(a, point, p)
def rowadd(a, b, f)
def terms(a)
def key(a)
def field(a, point, p)
def order(a)
def compositions(n, r)
def all_b(r, maximum)
def oracle(L, rho, b)
def oracle_row(L, rho, row)

```

Import this helper module from the stage that uses it.

[s01_generate.py](s01_generate.py)

The program generates bounded coupled vacuum families and reverse constructions from their exact masters.

The module defines these callable interfaces:

```python

def sha(p)
def write(p, v)
def gzwrite(p, records)
def profiles()
def splits()
def integral(L, b)
def sources(L, rho)
class UnluckySample
def generate(L, profile, rho)
def main()

```

The imported project modules are `s00_exact`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
DATA = HERE.parent

```

The command accepts these parser options:

- `'--loops'`: type=int; nargs='+'; default=list(range(2, 13)).
- `'--profiles'`: type=int; nargs='+'.

These calls show the stored input and output interface:

```python

tmp.write_text(json.dumps(v, indent=2, sort_keys=True) + '\n', encoding='utf-8')
(mb / 'masters.txt').write_text('\n'.join((m['expression'] for m in basis['masters'])) + '\n', encoding='utf-8')
done.read_text(encoding='utf-8')
p.read_bytes()

```

[s02_run_generation.sh](s02_run_generation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraLoopGeneration
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o integrals/higher_loops/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/higher_loops/s01_generate.py "$@"

```

[s03_validate.py](s03_validate.py)

The file provides independent identity and reverse-record checks, including convergent radial integrals.

The module defines these callable interfaces:

```python

def read(p)
def rows(p)
def parse(text)
def rational(text, point)
def mod(text, d, m, p)
def field(terms, s)
def addrow(row, src, f, p)
def source_poly(text)
def exact_source_form(e, L, rho)
def identity_check(e, L, rho)
def quadrature(definition, basis)
def check_family(path, numeric=False)
def main()

```

The imported external packages are `mpmath`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
D = mp.mpf(1) + mp.mpf(1) / (2 * L)

```

The command accepts these parser options:

- `'--pilot'`: action='store_true'.

These calls show the stored input and output interface:

```python

p.read_text(encoding='utf-8')
(DATA / name).read_bytes()

```

[s04_run_validation.sh](s04_run_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraLoopCheck
#$ -l h_rt=02:00:00,h_data=4G
#$ -j y
#$ -o integrals/higher_loops/validation_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/higher_loops/s03_validate.py "$@"

```

[s05_integrate.py](s05_integrate.py)

The program extends canonical catalogs and the existing grouped split after independent validation.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def sha(p)
def rows(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
MODEL = ROOT / 'ML_model_seed_selection'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n', encoding='utf-8')
(DATA / 'README.md').write_text(text, encoding='utf-8')
p.write_text(s, encoding='utf-8')
p.read_text(encoding='utf-8')
p.read_bytes()

```

[s06_run_all_loops.sh](s06_run_all_loops.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraAllLoopData
#$ -l h_rt=02:00:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/higher_loops/full_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"$GEN_PYTHON" integrals/higher_loops/s01_generate.py --loops 2 12 --profiles 1 3
"$GEN_PYTHON" integrals/higher_loops/s03_validate.py --pilot
"$GEN_PYTHON" integrals/higher_loops/s01_generate.py
"$GEN_PYTHON" integrals/higher_loops/s03_validate.py
"$GEN_PYTHON" integrals/higher_loops/s05_integrate.py

```

[s07_update_report.py](s07_update_report.py)

The program finalizes the report after both expanded-data tests pass; keep immutable data citations.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = ROOT / 'report'

```

The command accepts these parser options:

- `'--data-commit'`: required=True.
- `'--test-commit'`: required=True.

These calls show the stored input and output interface:

```python

(REPORT / 'higher_loops.tex').write_text((HERE / 'report_section_template.tex').read_text(encoding='utf-8'), encoding='utf-8')
path.read_text(encoding='utf-8')
(HERE / 'ml_roles_section_template.tex').read_text(encoding='utf-8')
path.write_text(s, encoding='utf-8')
make.read_text(encoding='utf-8')
make.write_text(text, encoding='utf-8')
path.write_text(text, encoding='utf-8')
bib.read_text(encoding='utf-8')
bib.write_text(b, encoding='utf-8')
report_readme.read_text(encoding='utf-8')
report_readme.write_text(notes, encoding='utf-8')
(HERE / 'report_update.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
(HERE / 'report_section_template.tex').read_text(encoding='utf-8')
(REPORT / (name + '.tex')).read_text(encoding='utf-8')
p.read_bytes()

```

[s08_finalize_training.py](s08_finalize_training.py)

The program validates both expanded-data models and describe the current trained release.

The module defines these callable interfaces:

```python

def read(p)
def write(p, o)
def sha(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(o, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
(folder / 'README.md').write_text(text.rstrip() + '\n', encoding='utf-8')
rp.read_text(encoding='utf-8')
rp.write_text(rt, encoding='utf-8')
p.read_bytes()

```

[s09_run_training_validation.sh](s09_run_training_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraAllLoopModelsCheck
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/higher_loops/training_validation_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/higher_loops/s08_finalize_training.py

```

[s10_validate_collection.py](s10_validate_collection.py)

The program audits links and source hashes across the complete expanded collection.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def link(value)
def rows(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
DATA = HERE.parent

```

The command accepts these parser options:

- `'--family'`: action='append'.
- `'--compare-source'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

(DATA / 'validation_summary.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
original.write_bytes(old.read_bytes())
old.read_bytes()

```

[s11_run_collection_audit.sh](s11_run_collection_audit.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCollectionAudit
#$ -l h_rt=00:30:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/higher_loops/collection_audit.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/s02_validate.py

```

[s12_finalize_tests.py](s12_finalize_tests.py)

The program records independently checked frozen tests and update affected READMEs.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def write(p, o)
def replace_tail(p, marker, text)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(o, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.write_text(s + '\n\n' + marker + '\n' + text.strip() + '\n', encoding='utf-8')
root.read_text(encoding='utf-8')
root.write_text(s, encoding='utf-8')
p.read_text(encoding='utf-8')
p.write_text(s, encoding='utf-8')
p.write_text(text, encoding='utf-8')
p.read_bytes()

```

[s13_build_report.sh](s13_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandedReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/higher_loops/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/higher_loops/s07_update_report.py "$@"
make -C report

```

[s14_stage_data.sh](s14_stage_data.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraStageData
#$ -l h_rt=00:30:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o .tools/stage_expanded_data.log
set -euo pipefail
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
if (( $# )); then
  git -c gc.auto=0 add -A -- "$@"
else
  git -c gc.auto=0 add -A -- integrals
fi
git diff --cached --shortstat

```

## Data and supporting files

- [collection_audit.log](collection_audit.log): This file records checks of the corresponding calculation.

- [full_scheduler.log](full_scheduler.log): This file contains saved program messages.

- [generation_summary.json](generation_summary.json): This file contains structured records from the parent calculation.

- [integration_summary.json](integration_summary.json): This file contains structured records from the parent calculation.

- [ml_roles_section_template.tex](ml_roles_section_template.tex): This file contains a LaTeX document or document section.

- [original_validation_summary.json](original_validation_summary.json): This file contains structured records from the parent calculation.

- [pilot_summary.json](pilot_summary.json): This file contains structured records from the parent calculation.

- [pilot_validation.json](pilot_validation.json): This file contains structured records from the parent calculation.

- [progress.json](progress.json): This file contains structured records from the parent calculation.

- [report_build.log](report_build.log): This file contains saved program messages.

- [report_build_final.log](report_build_final.log): This file contains saved program messages.

- [report_section_template.tex](report_section_template.tex): This file contains a LaTeX document or document section.

- [report_update.json](report_update.json): This file contains structured records from the parent calculation.

- [request.json](request.json): This file contains structured records from the parent calculation.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [test_release.json](test_release.json): This file contains structured records from the parent calculation.

- [training_release.json](training_release.json): This file records training progress or training inputs.

- [training_validation_resume_scheduler.log](training_validation_resume_scheduler.log): This file records training progress or training inputs.

- [training_validation_scheduler.log](training_validation_scheduler.log): This file records training progress or training inputs.

- [validation.json](validation.json): This file records the completed validation checks.

- [validation_scheduler.log](validation_scheduler.log): This file contains saved program messages.
