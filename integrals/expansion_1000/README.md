# expansion 1000

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

[reduction_test_storage_before.py](reduction_test_storage_before.py)

The file provides shared held-out metrics, bounded outputs and exact sample arithmetic.

The module defines these callable interfaces:

```python

def test_config()
def status(stage, **extra)
def signature()
def write_npz(path, **arrays)
def write_gzip(path, objects)
def csv_write(path, records)
def parsed(text)
def literal_int(node)
def coefficient(text, point, prime)
def eval_terms(terms, point, prime)
def exact_row_check(before, source, pivot, after, p)
def ordered_indices(probabilities, ids)
def classify(probabilities, reference, ids)
def reliability(confidence, correct, bins=10)
def metric_summary(data)
def merge_arrays(parts)
def ratio_summary(records, policy)

```

The imported external packages are `numpy`.

The imported project modules are `s00_common`, `s01_state`, `s05_predict`.

These source constants locate inputs and outputs:

```python

TEST = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

np.savez_compressed(f, **arrays)

```

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
def xzwrite(p, records)
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

- `'--loops'`: type=int; nargs='+'; default=list(range(1, 13)).
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
#$ -N KiraExpand1000
#$ -l h_rt=24:00:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/full_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"$GEN_PYTHON" integrals/expansion_1000/s01_generate.py --loops 1 2 12 --profiles 351 352
"$GEN_PYTHON" integrals/expansion_1000/s03_validate.py --pilot
"$GEN_PYTHON" integrals/expansion_1000/s01_generate.py
"$GEN_PYTHON" integrals/expansion_1000/s03_validate.py

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
def check_task(item)
def checked_tasks(tasks, workers)
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
- `'--group'`: type=int; choices=(1, 2, 3).

These calls show the stored input and output interface:

```python

p.read_text(encoding='utf-8')
(DATA / name).read_bytes()
Path(__file__).read_bytes()

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
#$ -o integrals/expansion_1000/validation_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s03_validate.py "$@"

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
#$ -l h_rt=01:00:00,h_data=4G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/training_validation_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s08_finalize_training.py

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
#$ -l h_rt=02:00:00,h_data=4G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/collection_audit.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s05_integrate.py
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
#$ -o integrals/expansion_1000/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s07_update_report.py "$@"
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

[s15_generate_parallel.py](s15_generate_parallel.py)

The program generates disjoint loop-order groups on twelve allocated CPU slots.

The module defines these callable interfaces:

```python

def loop_group(L)
def guard()
def main()

```

The imported project modules are `s01_generate`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()

```

[s16_run_parallel_generation.sh](s16_run_parallel_generation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpand1000Par
#$ -pe shared 12
#$ -l h_rt=08:00:00,h_data=512M,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/parallel_12_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"$GEN_PYTHON" integrals/expansion_1000/s01_generate.py --loops 1 2 12 --profiles 351 352
"$GEN_PYTHON" integrals/expansion_1000/s03_validate.py --pilot
"$GEN_PYTHON" integrals/expansion_1000/s15_generate_parallel.py
"$GEN_PYTHON" integrals/expansion_1000/s03_validate.py

```

[s17_validate_readers.py](s17_validate_readers.py)

The program checks gzip/XZ readers and new record links without model updates.

The imported project modules are `s00_common`, `s01_data`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'reader_validation.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s18_run_reader_validation.sh](s18_run_reader_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraXZReadCheck
#$ -l h_rt=00:10:00,h_data=2G
#$ -j y
#$ -o integrals/expansion_1000/reader_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s17_validate_readers.py

```

[s19_compact_git.sh](s19_compact_git.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraGitCompact
#$ -l h_rt=01:00:00,h_data=2G
#$ -j y
#$ -o integrals/expansion_1000/git_compaction.log
set -euo pipefail
export LC_ALL=C
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
git rev-parse HEAD > integrals/expansion_1000/git_head_before_compaction.txt
git count-objects -v
git -c pack.threads=1 -c pack.windowMemory=64m -c pack.deltaCacheSize=16m -c pack.packSizeLimit=256m -c gc.auto=0 repack -a -d
git count-objects -v
test "$(git rev-parse HEAD)" = "$(cat integrals/expansion_1000/git_head_before_compaction.txt)"

```

[s20_publish_release.py](s20_publish_release.py)

The program publishes checked artifacts in the authorized data/model, test, report sequence.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def run(args)
def allocated(paths)
def guard()
def preflight(paths)
def stage_selected(names)
def staged_bytes()
def object_counts()
def compact_unpacked(commit)
def commit_staged(title)
def commit_and_push(title)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'stage'`: choices=['training', 'tests', 'report'].

These calls show the stored input and output interface:

```python

path.write_text(json.dumps(records, indent=2, sort_keys=True) + '\n', encoding='utf-8')
path.write_text(json.dumps(checks, indent=2, sort_keys=True) + '\n', encoding='utf-8')
record.write_text(json.dumps(published, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
p.read_bytes()

```

[s21_run_publication.sh](s21_run_publication.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraPublish
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/publication_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s20_publish_release.py "$@"

```

[s22_generate_group.py](s22_generate_group.py)

The program generates disjoint loop groups in three bounded scheduler array tasks.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_generate`, `s15_generate_parallel`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()

```

[s23_run_generation_groups.sh](s23_run_generation_groups.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandGroups
#$ -l h_rt=06:00:00,h_data=512M,h_vmem=4G
#$ -pe shared 4
#$ -t 1-3
#$ -tc 3
#$ -j y
#$ -o integrals/expansion_1000/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"${GEN_PYTHON}" integrals/expansion_1000/s22_generate_group.py

```

[s24_combine_groups.py](s24_combine_groups.py)

The program combines completed disjoint groups before independent mathematical validation.

The imported project modules are `s01_generate`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / ('compression_group_%d.json' % i)).read_text()
(HERE / ('group_%d_summary.json' % i)).read_text()
(HERE / 'compression_pilot.json').read_text()

```

[s25_run_group_validation.sh](s25_run_group_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandMathCheck
#$ -l h_rt=01:00:00,h_data=1G,h_vmem=16G
#$ -pe shared 12
#$ -j y
#$ -o integrals/expansion_1000/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"${GEN_PYTHON}" integrals/expansion_1000/s24_combine_groups.py
"${GEN_PYTHON}" integrals/expansion_1000/s03_validate.py --pilot
"${GEN_PYTHON}" integrals/expansion_1000/s03_validate.py

```

[s26_run_test_publication.sh](s26_run_test_publication.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPublishTests
#$ -l h_rt=06:00:00,h_data=2G
#$ -j y
#$ -o integrals/expansion_1000/test_publication_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
python3 - <<'CACHE'
import json
from pathlib import Path
assert json.loads(Path("integrals/expansion_1000/git_cache_refresh.json").read_text())["status"]=="verified_partial_git_cache_active"
CACHE
.tools/seed-model/venv/bin/python integrals/expansion_1000/s12_finalize_tests.py
.tools/seed-model/venv/bin/python integrals/expansion_1000/s20_publish_release.py tests

```

[s27_run_report_update.sh](s27_run_report_update.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReportSources
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import hashlib,json,re,subprocess,sys
from pathlib import Path
phase=Path("integrals/expansion_1000")
p=json.loads((phase/"publication.json").read_text())
assert p["training"]["status"]==p["tests"]["status"]=="pushed"
subprocess.run([sys.executable,str(phase/"s07_update_report.py"),"--data-commit",p["training"]["commit"],"--test-commit",p["tests"]["commit"]],check=True)
text=Path("report/report.tex").read_text()
abstract=re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",text,re.S).group(1)
assert hashlib.sha256(abstract.encode()).hexdigest()==json.loads((phase/"request.json").read_text())["abstract_sha256"]
PY
make -C report

```

[s28_compress_records.py](s28_compress_records.py)

The program compresss completed new families before the final independent checks.

The module defines these callable interfaces:

```python

def one_family(path)
def main()

```

The imported project modules are `s01_generate`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

manifest.read_text()
tmp.write_bytes(compressed)
pending.read_text()
p.read_bytes()

```

[s29_run_compression.sh](s29_run_compression.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCompressNew
#$ -t 1-3
#$ -tc 3
#$ -pe shared 4
#$ -l h_rt=03:00:00,h_data=512M,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s28_compress_records.py

```

[s30_run_compression_pilot.sh](s30_run_compression_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCompressPilot
#$ -l h_rt=00:10:00,h_data=512M,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/compression_pilot.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,"integrals/expansion_1000")
from s28_compress_records import one_family,HERE,DATA,write,sha
p=DATA/"master_to_target/families/vacuum_L12_profile351"
first=one_family(p);digest=sha(p/"manifest.json")
second=one_family(p);assert first==second and digest==sha(p/"manifest.json")
assert not (p/".compression_pending.json").exists()
result=dict(status="passed",family=p.name,compression=first,idempotent=True,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
write(HERE/"compression_pilot.json",result)
print(json.dumps(result))
PY

```

[s31_benchmark_cpu_threads.py](s31_benchmark_cpu_threads.py)

The program measures CPU thread scaling on existing training examples without updating weights.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s01_data`, `s02_model`, `s13_batch`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = ROOT / 'ML_model_seed_selection'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(warm, map_location='cpu', weights_only=False)
(HERE / 'cpu_thread_pilot.json').write_text(json.dumps(out, indent=2) + '\n')
p.read_bytes()

```

[s32_run_cpu_thread_pilot.sh](s32_run_cpu_thread_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraThreadPilot
#$ -pe shared 4
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/cpu_thread_pilot.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s31_benchmark_cpu_threads.py

```

[s33_benchmark_reduction_threads.py](s33_benchmark_reduction_threads.py)

The program measures reduction-training CPU threads using saved training states only.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_common`, `s03_model`, `s10_train_all_loops`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = ROOT / 'ML_model_reduction'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(warm, map_location='cpu', weights_only=False)
(HERE / 'reduction_cpu_thread_pilot.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s34_run_reduction_thread_pilot.sh](s34_run_reduction_thread_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraRedThreadPilot
#$ -pe shared 4
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/reduction_cpu_thread_pilot.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s33_benchmark_reduction_threads.py

```

[s35_run_validation_groups.sh](s35_run_validation_groups.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraMathGroups
#$ -t 1-3
#$ -pe shared 4
#$ -l h_rt=01:00:00,h_data=1G,h_vmem=8G
#$ -j y
#$ -o integrals/expansion_1000/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s03_validate.py --group "$SGE_TASK_ID"

```

[s36_combine_validation.py](s36_combine_validation.py)

The program combines disjoint, independently checked family groups without repeating calculations.

The module defines these callable interfaces:

```python

def read(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
(HERE / 's03_validate.py').read_bytes()
Path(__file__).read_bytes()
(HERE / ('validation_group_%d.json' % g)).read_bytes()

```

[s37_finalize_validation.sh](s37_finalize_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraMathComplete
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
#$ -o integrals/expansion_1000/validation_combination.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s03_validate.py --pilot
.tools/seed-model/venv/bin/python integrals/expansion_1000/s36_combine_validation.py

```

[s38_check_parallel_preparation.py](s38_check_parallel_preparation.py)

The program compares parallel preparation with saved training arrays, without model updates.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s00_common`, `s02_prepare_data`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = ROOT / 'ML_model_reduction'

```

This entry point uses the paths and options set in its source.

[s39_run_preparation_check.sh](s39_run_preparation_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraPreparationCheck
#$ -pe shared 4
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=8G
#$ -j y
#$ -o integrals/expansion_1000/parallel_preparation_check.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s17_validate_readers.py
.tools/seed-model/venv/bin/python integrals/expansion_1000/s38_check_parallel_preparation.py

```

[s40_validate_reduction_checkpoint.sh](s40_validate_reduction_checkpoint.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionWeights
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/reduction_checkpoint_check.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/model_test/s09_validate_checkpoint.py

```

[s41_check_git_blob_estimate.py](s41_check_git_blob_estimate.py)

The program checks the publication size estimate against bounded temporary Git objects.

The module defines these callable interfaces:

```python

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

(HERE / 'git_blob_estimate_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
(HERE / 's20_publish_release.py').read_bytes()

```

[s42_compare_storage_scans.py](s42_compare_storage_scans.py)

The program compares equivalent storage scans on immutable training features.

The module defines these callable interfaces:

```python

def old_scan(root)
def new_scan(root)
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

(HERE / 'storage_scan_comparison.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

```

[s43_run_storage_scan_check.sh](s43_run_storage_scan_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraStorageScanCheck
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=2G
#$ -j y
#$ -o integrals/expansion_1000/storage_scan_comparison.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s42_compare_storage_scans.py

```

[s44_verify_storage_scan_resume.py](s44_verify_storage_scan_resume.py)

The program proves that the resource-only scan update preserves predictive code and resume state.

The module defines these callable interfaces:

```python

def sha(p)
def read(p)
def predictive_ast(p)
def main()

```

The imported external packages are `torch`.

The imported project modules are `s42_compare_storage_scans`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = ROOT / 'ML_model_seed_selection'
ARCHIVE = MODEL / 'runs/storage_scan_resume'

```

The command accepts these parser options:

- `'--before-resume'`: action='store_true'.

These calls show the stored input and output interface:

```python

(ARCHIVE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
(fixture / 'plain').write_bytes(b'a' * 31)
(fixture / '.hidden').write_bytes(b'b' * 17)
(fixture / 'nested/data').write_bytes(b'c' * 53)
torch.load(ARCHIVE / 'checkpoint_before.pt', map_location='cpu', weights_only=False)
p.read_bytes()
(ARCHIVE / 's01_data_before.py').read_text()
(MODEL / 's01_data.py').read_text()

```

[s45_resume_seed_training.sh](s45_resume_seed_training.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedResume
#$ -pe shared 4
#$ -l h_rt=12:00:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/storage_scan_resume_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s44_verify_storage_scan_resume.py --before-resume
exec bash ML_model_seed_selection/s15_run_all_loops.sh

```

[s46_validate_report_release.py](s46_validate_report_release.py)

The program checks the rendered report against the frozen releases before publication.

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

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(REPORT / 'report.tex').read_text(encoding='utf-8')
(REPORT / 'references.bib').read_text(encoding='utf-8')
(REPORT / 'report.log').read_text(encoding='utf-8', errors='replace')
pdf.read_bytes()
(HERE / 'report_validation.json').write_text(json.dumps(checks, indent=2, sort_keys=True) + '\n', encoding='utf-8')
(HERE / 'report_update.json').write_text(json.dumps(update, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
p.read_bytes()

```

[s47_run_report_publication.sh](s47_run_report_publication.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPublishReport
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/report_publication_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s46_validate_report_release.py
.tools/seed-model/venv/bin/python integrals/expansion_1000/s20_publish_release.py report

```

[s48_refresh_git_cache.py](s48_refresh_git_cache.py)

The program replaces a redundant full Git object cache with a verified partial clone.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def git(where, *args, network=True)
def refs(where)
def objects(where)
def working_artifacts()
def allocated(where)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / '.tools/git-migration'
OLD = ROOT / '.git'
NEW = CACHE / 'partial/.git'
BACKUP = CACHE / 'previous-metadata'
GIT = '/u/local/apps/git/2.40.0/bin/git'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'git_cache_refresh.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')

```

[s49_run_git_cache_refresh.sh](s49_run_git_cache_refresh.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGitCache
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/git_cache_refresh_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 262144
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s48_refresh_git_cache.py

```

[s50_check_publication_storage_guard.py](s50_check_publication_storage_guard.py)

The program checks publication storage bounds against actual allocated fixture sizes.

The module defines these callable interfaces:

```python

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

(HERE / 'publication_storage_guard_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
(base / 'immutable.bin').write_bytes(b'x' * 32768)
(base / '.git' / 'new_blob').write_bytes(bytes(range(256)) * 4096)
(base / 'phase' / 'new_record').write_bytes(b'record\n' * 10000)
(HERE / 's20_publish_release.py').read_bytes()

```

[s51_check_partial_clone_staging.py](s51_check_partial_clone_staging.py)

The program checks bounded staging in a blob-filtered clone without fetching unchanged data.

The module defines these callable interfaces:

```python

def git(root, *args, **kw)
def objects(root)
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

(HERE / 'partial_clone_staging_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
(origin / 'integrals/immutable.bin').write_bytes(bytes(range(256)) * 4096)
(origin / 'report/report.tex').write_text('old report\n')
(origin / 'report/old.txt').write_text('remove this fixture file\n')
(work / 'report/report.tex').write_text('new report with a changed value\n')
(work / 'report/new [note].txt').write_text('new fixture record\n')
(HERE / 's20_publish_release.py').read_bytes()

```

[s52_complete_release.py](s52_complete_release.py)

The program checks the local report review and publish the final release records.

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
doc.read_text(encoding='utf-8')
doc.write_text(s, encoding='utf-8')
p.read_text(encoding='utf-8')
p.read_bytes()

```

[s53_run_release_completion.sh](s53_run_release_completion.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReleaseComplete
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o .tools/final-release/publication.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s52_complete_release.py

```

[seed_test_storage_before.py](seed_test_storage_before.py)

The program evaluates the frozen trained model on every held-out target and save reproducible predictions.

The module defines these callable interfaces:

```python

def sha(path)
def write_json(path, data)
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_metrics`, `s01_data`, `s02_model`, `s04_predict`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
MODEL = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

temp.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')

```

## Data and supporting files

This folder contains 111 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.json`: 67 entries.

- `.log`: 19 entries.

- `.log.before_partial_commit_fix`: 2 entries.

- `.o15067261.1`: 1 entries.

- `.o15067261.2`: 1 entries.

- `.o15067261.3`: 1 entries.

- `.o15067268`: 1 entries.

- `.o15067508.1`: 1 entries.

- `.o15067508.2`: 1 entries.

- `.o15067508.3`: 1 entries.

- `.o15069248.1`: 1 entries.

- `.o15069248.2`: 1 entries.

- `.o15069248.3`: 1 entries.

- `.po15067261.1`: 1 entries.

- `.po15067261.2`: 1 entries.

- `.po15067261.3`: 1 entries.

- `.po15067268`: 1 entries.

- `.po15067508.1`: 1 entries.

- `.po15067508.2`: 1 entries.

- `.po15067508.3`: 1 entries.

- `.po15069248.1`: 1 entries.

- `.po15069248.2`: 1 entries.

- `.po15069248.3`: 1 entries.

- `.tex`: 2 entries.

- `.txt`: 1 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
