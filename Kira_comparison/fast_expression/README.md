# fast expression

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

[connect2kira.patch](connect2kira.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/connect2kira.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_prepare.py](s00_prepare.py)

The program fixs new timing cases and resource limits before measuring the new interface.

The module defines these callable interfaces:

```python

def sha(p)
def rank(s)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'ML_model_seed_selection/split_manifest.json').read_text()
(HERE.parent / 'acceleration/plan.json').read_text()
(HERE.parent / 'plan.json').read_text()
p.write_text(json.dumps(plan, indent=2) + '\n')
p.read_bytes()
p.read_text()

```

[s01_reap_child.h](s01_reap_child.h)

The file provides sPDX-License-Identifier: GPL-3.0-or-later.

The required headers are `cerrno`, `chrono`, `csignal`, `sys/wait.h`, `thread`, `unistd.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s02_reap_test.cpp](s02_reap_test.cpp)

The file provides sPDX-License-Identifier: GPL-3.0-or-later.

The required headers are `s01_reap_child.h`, `cassert`, `iostream`.

The matching build script compiles this file into an executable.

Use the parent stage guide for the build order and input records.

[s03_build.py](s03_build.py)

The program builds an isolated stock Kira with responsive, bounded Fermat shutdown.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

source.read_text()
modified.write_text(text)
(HERE / 'reap_validation.json').write_text(json.dumps(checks, indent=2) + '\n')
(HERE / 'build.json').write_text(json.dumps(record, indent=2) + '\n')
(build / 'compile_commands.json').read_text()
p.read_bytes()

```

[s04_build.sh](s04_build.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitBuild
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s03_build.py

```

[s05_worker.py](s05_worker.py)

The program runs unchanged seed selection and exact checks with a chosen Kira binary.

The module defines these callable interfaces:

```python

def kira_run(w, plan)

```

The imported project modules are `s01_common`, `s02_worker`, `s78_expression_controls_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACC = HERE.parent / 'acceleration'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')

```

[s06_run.py](s06_run.py)

The program rotates complete cold trials and retain failures within fixed resource limits.

The module defines these callable interfaces:

```python

def sha(p)
def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s13_records`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACC = HERE.parent / 'acceleration'

```

The command accepts these parser options:

- `'--partition'`: choices=['development', 'test']; required=True.
- `'--case'`: type=int; required=True.
- `'--size'`: type=int; required=True.
- `'--repetitions'`: type=int; default=1.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'plan.json').read_text()
(HERE / 'freeze.json').read_text()
p.read_bytes()
record.read_text()
path.read_text(errors='replace')
pathlib.Path('/proc/cpuinfo').read_text()

```

[s07_development.sh](s07_development.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitDev
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_FAST_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-fast-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_FAST_SCRATCH"' EXIT
for case in 0 1 2; do
 .tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s06_run.py --partition development --case "$case" --size 1 --repetitions 1
done

```

[s08_freeze.py](s08_freeze.py)

The program freezes all scientific inputs and executables after development checks.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s01_common`, `s13_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACC = HERE.parent / 'acceleration'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'freeze.json').write_text(json.dumps(out, indent=2) + '\n')
(HERE / 'plan.json').read_text()
(HERE / 'development_validation.json').read_text()
p.read_bytes()

```

[s09_test_array.sh](s09_test_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitTest
#$ -l h_rt=01:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_FAST_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-fast-${JOB_ID}-${SGE_TASK_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_FAST_SCRATCH"' EXIT
index=$((SGE_TASK_ID-1)); case=$((index/2))
if (( index % 2 == 0 )); then size=1; else size=16; fi
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s06_run.py --partition test --case "$case" --size "$size" --repetitions 5

```

[s10_audit.py](s10_audit.py)

The program checks raw Kira coefficients and unchanged seed decisions.

The module defines these callable interfaces:

```python

def mapped(p)
def sha(p)
def main()

```

The imported project modules are `s13_records`, `s36_evidence`, `s80_expression_test_audit`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACC = HERE.parent / 'acceleration'

```

The command accepts these parser options:

- `'--stage'`: required=True.

These calls show the stored input and output interface:

```python

(HERE / (a.stage + '_validation.json')).write_text(json.dumps(validation, indent=2) + '\n')
(HERE / (a.stage + '_validation.json')).read_text()
(HERE / 'freeze.json').read_text()
p.read_bytes()
(HERE / 'build.json').read_text()

```

[s11_summary.py](s11_summary.py)

The program reports all completions and group-resampled paired complete-time ratios.

The module defines these callable interfaces:

```python

def read(p)
def good(r)
def main()

```

The imported project modules are `s13_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--stage'`: required=True.

These calls show the stored input and output interface:

```python

(HERE / (a.stage + '_summary.json')).write_text(json.dumps(out, indent=2) + '\n')
p.read_text()
(HERE / (a.stage + '_validation.json')).read_bytes()

```

[s12_check.sh](s12_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitCheck
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s10_audit.py --stage "$1"
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s11_summary.py --stage "$1"

```

[s13_records.py](s13_records.py)

The file provides lossless shared arrays keep repeated timing evidence within the storage cap.

The module defines these callable interfaces:

```python

def shared(value)
def compact(r)
def restore(v)
def read_record(p)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'shared' / (h + '.json.gz')).read_bytes()

```

[s14_report.py](s14_report.py)

The program writes measured results, a figure and the scientific report after validation.

The module defines these callable interfaces:

```python

def read(p)
def main()

```

The imported external packages are `matplotlib`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = ROOT / 'report'

```

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

(REPORT / 'kira_fast_expression.tex').write_text(text)
mainpath.read_text()
mainpath.write_text(maintext)
bib.read_text()
bib.write_text(b)
make.read_text()
make.write_text(t)
(HERE / 'report_values.json').write_text(json.dumps(values, indent=2) + '\n')
p.read_text()

```

[s15_confirm.sh](s15_confirm.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitFreeze
#$ -l h_rt=00:05:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s08_freeze.py
QSUB_FAST="${SGE_ROOT:-/u/systems/UGE8.6.4}/bin/${SGE_ARCH:-lx-amd64}/qsub"
TEST_FAST=$("$QSUB_FAST" -terse -t 1-24 -tc 2 -o .tools/kira-fast-expression Kira_comparison/fast_expression/s09_test_array.sh)
CHECK_FAST=$("$QSUB_FAST" -terse -hold_jid "${TEST_FAST%%.*}" -o .tools/kira-fast-expression/test_check.log Kira_comparison/fast_expression/s12_check.sh test)
python - "$TEST_FAST" "$CHECK_FAST" <<'PY'
import json,pathlib,sys,datetime
pathlib.Path('Kira_comparison/fast_expression/execution.json').write_text(json.dumps(dict(test_job=sys.argv[1],audit_job=sys.argv[2],concurrency=2,submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
print(sys.argv[1:])
PY

```

[s16_document.py](s16_document.py)

The program updates the experiment and project READMEs from audited results.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(t)
(HERE / 'test_summary.json').read_text()
(HERE / 'test_validation.json').read_text()

```

[s17_build_report.sh](s17_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitReport
#$ -l h_rt=00:08:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s21_report_compat.py --data-commit "$1"
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s20_report_finish.py --data-commit "$1"
make -C report

```

[s18_release.py](s18_release.py)

The program checks frozen inputs, all trial records, resource bounds and release readiness.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s03_run`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/report.tex').read_text()
(HERE / 'release_validation.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'plan.json').read_text()
(HERE / 'freeze.json').read_text()
(HERE / 'execution.json').read_text()
(HERE / (stage + '_validation.json')).read_text()
p.read_text()
p.read_bytes()
(HERE / 'scheduler_amendment_02.json').read_text()

```

[s19_finalize.sh](s19_finalize.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitRelease
#$ -l h_rt=00:08:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s18_release.py
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s16_document.py
python - <<'PY'
from pathlib import Path
import json
p=Path('.tools/kira-fast-publication/completion.json')
assert not p.exists()
p.write_text(json.dumps(dict(stage="comparisons_validated",expected_trials=480,declared_records=492,published_blob_upper_bytes=0,prior_commit="99ccf5b6bf4bc1beab307cddf684c40d5ab19e5d"),indent=2)+"\n")
print("Ready for code/data publication and report rendering.")
PY

```

[s20_report_finish.py](s20_report_finish.py)

The program applies final report formatting and state the measured completion cohorts.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = ROOT / 'report'

```

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(t)
(HERE / 'test_summary.json').read_text()
(HERE / 'scheduler_amendment.json').read_text()

```

[s21_report_compat.py](s21_report_compat.py)

The program renders the frozen report script with the cluster Matplotlib API.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

SOURCE = Path(__file__).with_name('s14_report.py')

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

SOURCE.read_text()

```

## Data and supporting files

- [build.json](build.json): This file contains structured records from the parent calculation.

- [development_summary.json](development_summary.json): This file contains structured records from the parent calculation.

- [development_validation.json](development_validation.json): This file contains structured records from the parent calculation.

- [execution.json](execution.json): This file contains structured records from the parent calculation.

- [figure_values.csv](figure_values.csv): This file supports the calculation described in the parent guide.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [plan.json](plan.json): This file contains structured records from the parent calculation.

- [reap_validation.json](reap_validation.json): This file contains structured records from the parent calculation.

- [release_validation.json](release_validation.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [scheduler_amendment.json](scheduler_amendment.json): This file contains structured records from the parent calculation.

- [scheduler_amendment_02.json](scheduler_amendment_02.json): This file contains structured records from the parent calculation.

- [test_summary.json](test_summary.json): This file contains structured records from the parent calculation.

- [test_validation.json](test_validation.json): This file contains structured records from the parent calculation.

## Child folders

- [development](development/README.md).

- [evidence](evidence/README.md).

- [shared](shared/README.md).

- [test](test/README.md).
