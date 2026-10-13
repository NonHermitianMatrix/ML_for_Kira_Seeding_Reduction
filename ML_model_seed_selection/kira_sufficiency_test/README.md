# kira sufficiency test

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

[s00_check_kira.py](s00_check_kira.py)

The file provides small exact Kira fixtures before testing predicted seed sets.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORK = ROOT / '.tools/kira-seed-sufficiency'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'fixture_runs.json').write_text(json.dumps(results, indent=2) + '\n')
(w / 'system.kira').write_text(system + '\n')
(w / 'targets').write_text('\n'.join(selected) + '\n')
(w / 'masters').write_text('\n'.join(masters) + '\n')
p.read_text(errors='replace')
(w / 'run.log').read_text(errors='replace')

```

[s01_run_fixtures.sh](s01_run_fixtures.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedFixture
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/fixture_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s00_check_kira.py

```

[s02_common.py](s02_common.py)

The file provides frozen inputs, bounded exact rational arithmetic, and seed-filtered systems.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def write(p, v)
def rows(p)
def family_file(fid, name)
def index_key(a)
def load_family(meta, prediction_entry, limit=None)
def literal(n)
def validate_expression(s)
def add(a, b, sign=1)
def mul(a, b)
def power(a, n)
def normalize(a, b)
def rational(s)
def exact_equal(left, right)
def exact_zero(s)
def clear_caches()
def selected_blocks(family)

```

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
DATA = ROOT / 'integrals'
WORK = ROOT / '.tools/kira-seed-sufficiency'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

tmp.write_text(json.dumps(v, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
Path(p).read_text(encoding='utf-8')

```

[s03_kira_adapter.py](s03_kira_adapter.py)

The program exports disjoint seed selections and read Kira's exact symbolic reductions.

The module defines these callable interfaces:

```python

def allocated(p)
def batches(blocks, limit=50000)
def export(family, blocks, w, quotient=True)
def run_once(w, timeout=600, scratch_limit=67108864)
def run_kira(w, timeout=600, scratch_limit=67108864)
def parse_output(path)
def assess(family, manifest, output, reference_by_id)
def assess_span(family, manifest, output, reference_by_id)

```

The imported project modules are `s02_common`, `s08_verify`, `s22_coefficient_reader`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'targets').write_text(''.join(('%d\n' % i for i in targetmap)))
(w / 'masters').write_text(''.join(('%d\n' % i for i in basis)))
(w / 'jobs.yaml').write_text(JOBS)
(w / 'run.log').read_text(errors='replace')

```

[s04_run_pilot.py](s04_run_pilot.py)

The program runs bounded mathematical checks and representative held-out Kira reductions.

The module defines these callable interfaces:

```python

def arithmetic_checks()
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s03_kira_adapter`, `s08_verify`.

This entry point uses the paths and options set in its source.

[s05_run_pilot.sh](s05_run_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedPilot
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/pilot_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s04_run_pilot.py

```

[s06_evaluate.py](s06_evaluate.py)

The program freezes the solver protocol and evaluate disjoint held-out systems on Hoffman.

The module defines these callable interfaces:

```python

def protocol()
def output_allocated(folder)
def bounded_gzip(path, binary=False)
def save_gz(path, value)
def process(meta, prediction_entry, dest, scratch)
def worker(index)

```

The imported project modules are `s03_kira_adapter`, `s08_verify`.

The command accepts these parser options:

- `'--freeze'`: action='store_true'.
- `'--worker'`: type=int.

These calls show the stored input and output interface:

```python

Path('/proc/meminfo').read_text()

```

[s07_run_evaluation.sh](s07_run_evaluation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedEval
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 1-16
#$ -tc 16
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s06_evaluate.py --worker "$((SGE_TASK_ID-1))"

```

[s08_verify.py](s08_verify.py)

The file provides independent finite-field checks, using a nonrecursive rational-expression reader.

The module defines these callable interfaces:

```python

def evaluate(expression, variables, prime)
def check_records(records, references)
def nonzero_witness(expression, samples)
def reduced(row, basis)
def insert_row(row, basis)
def check_span_records(family, blocks, records, references)

```

The imported project modules are `s02_common`, `s22_coefficient_reader`.

Import this helper module from the stage that uses it.

[s09_check_import.py](s09_check_import.py)

The program checks supported symbolic-system import modes on the small legacy-family pilot.

The imported project modules are `s03_kira_adapter`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'system.kira').read_text()
(w / 'system.kira').write_text(content)
(w / 'jobs.yaml').write_text(JOBS.replace('otf: false', 'otf: true'))

```

[s10_run_import_checks.sh](s10_run_import_checks.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraImportCheck
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/import_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s09_check_import.py

```

[s11_summarize.py](s11_summarize.py)

The program validates saved solver records, then summarize exact target completion.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s06_evaluate`, `s08_verify`, `s32_verify_export`.

This entry point uses the paths and options set in its source.

[s12_run_summary.sh](s12_run_summary.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedSummary
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/summary_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s11_summarize.py

```

[s13_plot_results.py](s13_plot_results.py)

The program plots exact seed sufficiency and the selected candidate fractions.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

The imported project modules are `s02_common`.

This entry point uses the paths and options set in its source.

[s14_run_plots.sh](s14_run_plots.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedPlots
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/plot_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s13_plot_results.py

```

[s15_update_report.py](s15_update_report.py)

The program updates the scientific report from the completed Kira sufficiency test.

The module defines these callable interfaces:

```python

def main(commit)

```

The imported project modules are `s02_common`.

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

main.read_text()
(out / 'seed_kira_test.tex').write_text(METHOD + results)
p.read_text()
p.write_text(text)
main.write_text(s)
bib.read_text()
bib.write_text(text)

```

[s16_check_target_order.py](s16_check_target_order.py)

The program checks direct target ordering without changing seeds or source identities.

The imported project modules are `s03_kira_adapter`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'system.kira').write_text('\n'.join(lines) + '\n')
(w / 'masters').write_text(''.join((str(permutation[i]) + '\n' for i in oldmasters)))
(w / 'targets').write_text(''.join((str(permutation[i]) + '\n' for i in oldtargets)))
(w / 'system.kira').read_text()

```

[s17_run_ordering_check.sh](s17_run_ordering_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTargetOrder
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/ordering_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s16_check_target_order.py

```

[s18_check_master_span.py](s18_check_master_span.py)

The program tests exact membership in the span of identities and specified masters.

The imported project modules are `s03_kira_adapter`.

Import this helper module from the stage that uses it.

[s19_run_span_check.sh](s19_run_span_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraMasterSpan
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/span_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s18_check_master_span.py

```

[s20_validate_span_pilot.py](s20_validate_span_pilot.py)

The program validates exact master-span decisions independently before the full run.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s06_evaluate`.

This entry point uses the paths and options set in its source.

[s21_run_span_validation.sh](s21_run_span_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSpanValidate
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/span_validation_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s20_validate_span_pilot.py

```

[s22_coefficient_reader.py](s22_coefficient_reader.py)

The file provides bounded, nonrecursive parsing of Kira rational expressions.

The module defines these callable interfaces:

```python

def parse(expression)
def small_parse(expression)
def tokens(expression)
def validate_output(expression)
def modular(expression, variables, prime)

```

These source constants locate inputs and outputs:

```python

TOKEN = re.compile('\\s*(\\*\\*|[()+*/^-]|[0-9]+|[A-Za-z][A-Za-z_0-9]*)')
OPS = {'+': 1, '-': 1, '*': 2, '/': 2, 'u+': 3, 'u-': 3, '**': 4}

```

Import this helper module from the stage that uses it.

[s23_check_quotient_order.py](s23_check_quotient_order.py)

The file provides bounded diagnostic of equivalent target-first quotient ordering.

The imported project modules are `s03_kira_adapter`, `s08_verify`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'system.kira').write_text('\n'.join(lines) + '\n')
(w / 'masters').write_text(''.join((str(permutation[i]) + '\n' for i in oldmasters)))
(w / 'targets').write_text(''.join((str(permutation[i]) + '\n' for i in oldtargets)))
(w / 'system.kira').read_text()

```

[s24_run_quotient_order.sh](s24_run_quotient_order.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraMasterSpan
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/quotient_ordering_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s23_check_quotient_order.py

```

[s25_finalize_readmes.py](s25_finalize_readmes.py)

The program writes completion descriptions only from independently validated test results.

The imported project modules are `s02_common`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(text)

```

[s26_validate_reader.py](s26_validate_reader.py)

The program checks the large-expression reader against the archived independent evaluator.

The imported project modules are `s02_common`, `s22_coefficient_reader`.

Import this helper module from the stage that uses it.

[s27_retry_small_batches.py](s27_retry_small_batches.py)

The program retries unresolved symbolic systems with independent, smaller target batches.

The module defines these callable interfaces:

```python

def small_batches(blocks)
def main(fid)

```

The imported project modules are `s06_evaluate`.

The command accepts these parser options:

- `'--family'`: default='box_profile_0168'.

[s28_run_small_batch_pilot.sh](s28_run_small_batch_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSmallBatch
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/small_batch_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s27_retry_small_batches.py

```

[s29_resume_small_batches.py](s29_resume_small_batches.py)

The program resumes the same frozen test with smaller box-family execution batches.

The module defines these callable interfaces:

```python

def process(meta, entry, dest, scratch)
def main(index)

```

The imported project modules are `s06_evaluate`, `s31_pack_small_batches`.

The command accepts these parser options:

- `'--worker'`: type=int; required=True.

[s30_run_small_batches.sh](s30_run_small_batches.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedSplit
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 1-16
#$ -tc 16
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s29_resume_small_batches.py --worker "$((SGE_TASK_ID-1))"

```

[s31_pack_small_batches.py](s31_pack_small_batches.py)

The program packs at most four independent small systems while preserving all equations.

The module defines these callable interfaces:

```python

def packed_batches(blocks)

```

The imported project modules are `s27_retry_small_batches`.

Import this helper module from the stage that uses it.

[s32_verify_export.py](s32_verify_export.py)

The program regenerates each actual Kira input from public targets and selected identities.

The module defines these callable interfaces:

```python

def prepare(meta)
def verify(state, manifest)

```

The imported project modules are `s02_common`.

Import this helper module from the stage that uses it.

[s33_output_budget.py](s33_output_budget.py)

The program bounds compressed writes to a documented 32 MiB worker allowance.

The module defines these callable interfaces:

```python

def bounded_gzip(path, binary=False)

```

The imported project modules are `s06_evaluate`.

Import this helper module from the stage that uses it.

[s34_resume_output_budget.py](s34_resume_output_budget.py)

The program resumes completed or stopped shards within the revised storage reserve.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s06_evaluate`, `s29_resume_small_batches`, `s33_output_budget`.

The command accepts these parser options:

- `'--worker'`: type=int; required=True.

These calls show the stored input and output interface:

```python

Path('/proc/meminfo').read_text()

```

[s35_run_output_resume.sh](s35_run_output_resume.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedResume
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 1-16
#$ -tc 16
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s34_resume_output_budget.py --worker "$((SGE_TASK_ID-1))"

```

[s36_resume_unfinished.py](s36_resume_unfinished.py)

The program finishes only shards left incomplete after the preceding execution.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s02_common`, `s34_resume_output_budget`.

The command accepts these parser options:

- `'--worker'`: required=True; type=int.

[s37_run_remaining.sh](s37_run_remaining.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRemaining
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 1-16
#$ -tc 16
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s36_resume_unfinished.py --worker "$((SGE_TASK_ID-1))"

```

[s38_output_budget_48.py](s38_output_budget_48.py)

The program bounds compressed writes to a documented 48 MiB worker allowance.

The module defines these callable interfaces:

```python

def bounded_gzip(path, binary=False)

```

The imported project modules are `s06_evaluate`.

Import this helper module from the stage that uses it.

[s39_resume_output_48.py](s39_resume_output_48.py)

The program resumes completed or stopped shards within the revised storage reserve.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s06_evaluate`, `s29_resume_small_batches`, `s38_output_budget_48`.

The command accepts these parser options:

- `'--worker'`: type=int; required=True.

These calls show the stored input and output interface:

```python

Path('/proc/meminfo').read_text()

```

[s40_finish_remaining.py](s40_finish_remaining.py)

The program finishes only shards left incomplete after the preceding execution.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s02_common`, `s39_resume_output_48`.

The command accepts these parser options:

- `'--worker'`: required=True; type=int.

[s41_run_remaining.sh](s41_run_remaining.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFinalCases
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 1-16
#$ -tc 8
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s40_finish_remaining.py --worker "$((SGE_TASK_ID-1))"

```

[s42_resume_ready.py](s42_resume_ready.py)

The program uses spare slots for finished shards while other earlier shards continue.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s02_common`, `s40_finish_remaining`.

The command accepts these parser options:

- `'--worker'`: required=True; type=int.

[s43_run_ready.sh](s43_run_ready.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReadyCases
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 1-16
#$ -tc 2
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s42_resume_ready.py --worker "$((SGE_TASK_ID-1))"

```

[s44_output_budget_80.py](s44_output_budget_80.py)

The program bounds compressed writes to a documented 80 MiB worker allowance.

The module defines these callable interfaces:

```python

def bounded_gzip(path, binary=False)

```

The imported project modules are `s06_evaluate`.

Import this helper module from the stage that uses it.

[s45_resume_large_output.py](s45_resume_large_output.py)

The program resumes completed or stopped shards within the revised storage reserve.

The module defines these callable interfaces:

```python

def main(index)

```

The imported project modules are `s06_evaluate`, `s29_resume_small_batches`, `s44_output_budget_80`.

The command accepts these parser options:

- `'--worker'`: type=int; required=True.

These calls show the stored input and output interface:

```python

Path('/proc/meminfo').read_text()

```

[s46_run_large_output.sh](s46_run_large_output.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLargeOutput
#$ -l h_rt=12:00:00,h_data=3G,h_vmem=4G
#$ -t 11-11
#$ -tc 1
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/scheduler/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s45_resume_large_output.py --worker "$((SGE_TASK_ID-1))"

```

## Data and supporting files

- [execution_overrides.json](execution_overrides.json): This file contains structured records from the parent calculation.

- [family_results.csv](family_results.csv): This file supports the calculation described in the parent guide.

- [fixture_runs.json](fixture_runs.json): This file contains structured records from the parent calculation.

- [fixture_scheduler.log](fixture_scheduler.log): This file contains saved program messages.

- [import_scheduler.log](import_scheduler.log): This file contains saved program messages.

- [input_regeneration_pilot.json](input_regeneration_pilot.json): This file contains structured records from the parent calculation.

- [ordering_scheduler.log](ordering_scheduler.log): This file contains saved program messages.

- [packing_validation.json](packing_validation.json): This file contains structured records from the parent calculation.

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

- [plot_scheduler.log](plot_scheduler.log): This file contains saved program messages.

- [protocol.json](protocol.json): This file contains structured records from the parent calculation.

- [quotient_ordering_scheduler.log](quotient_ordering_scheduler.log): This file contains saved program messages.

- [reader_validation.json](reader_validation.json): This file contains structured records from the parent calculation.

- [ready_resume_schedule.json](ready_resume_schedule.json): This file contains structured records from the parent calculation.

- [resource_limits.json](resource_limits.json): This file contains structured records from the parent calculation.

- [resource_limits_v2.json](resource_limits_v2.json): This file contains structured records from the parent calculation.

- [resource_limits_v3.json](resource_limits_v3.json): This file contains structured records from the parent calculation.

- [results.json](results.json): This file contains structured records from the parent calculation.

- [small_batch_scheduler.log](small_batch_scheduler.log): This file contains saved program messages.

- [span_scheduler.log](span_scheduler.log): This file contains saved program messages.

- [span_validation_scheduler.log](span_validation_scheduler.log): This file contains saved program messages.

- [summary_scheduler.log](summary_scheduler.log): This file contains saved program messages.

- [validation.json](validation.json): This file records the completed validation checks.

- [worker_00.json](worker_00.json): This file contains structured records from the parent calculation.

- [worker_01.json](worker_01.json): This file contains structured records from the parent calculation.

- [worker_02.json](worker_02.json): This file contains structured records from the parent calculation.

- [worker_03.json](worker_03.json): This file contains structured records from the parent calculation.

- [worker_04.json](worker_04.json): This file contains structured records from the parent calculation.

- [worker_05.json](worker_05.json): This file contains structured records from the parent calculation.

- [worker_06.json](worker_06.json): This file contains structured records from the parent calculation.

- [worker_07.json](worker_07.json): This file contains structured records from the parent calculation.

- [worker_08.json](worker_08.json): This file contains structured records from the parent calculation.

- [worker_09.json](worker_09.json): This file contains structured records from the parent calculation.

- [worker_10.json](worker_10.json): This file contains structured records from the parent calculation.

- [worker_11.json](worker_11.json): This file contains structured records from the parent calculation.

- [worker_12.json](worker_12.json): This file contains structured records from the parent calculation.

- [worker_13.json](worker_13.json): This file contains structured records from the parent calculation.

- [worker_14.json](worker_14.json): This file contains structured records from the parent calculation.

- [worker_15.json](worker_15.json): This file contains structured records from the parent calculation.

## Child folders

- [archive_coefficient_reductions](archive_coefficient_reductions/README.md).

- [archive_output_allowance](archive_output_allowance/README.md).

- [archive_output_allowance_v2](archive_output_allowance_v2/README.md).

- [archive_output_allowance_v3](archive_output_allowance_v3/README.md).

- [archive_span_large_batches](archive_span_large_batches/README.md).

- [archive_span_reader_v1](archive_span_reader_v1/README.md).

- [figures](figures/README.md).

- [import_checks](import_checks/README.md).

- [ordering_pilot](ordering_pilot/README.md).

- [pilot](pilot/README.md).

- [results](results/README.md).

- [scheduler](scheduler/README.md).

- [small_batch_pilot](small_batch_pilot/README.md).

- [span_pilot](span_pilot/README.md).
