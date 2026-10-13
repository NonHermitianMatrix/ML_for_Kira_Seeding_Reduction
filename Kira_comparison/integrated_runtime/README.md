# integrated runtime

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

[ephemeral_database.patch](ephemeral_database.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/dataBase.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_cached.patch](reduction_cached.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_cost.patch](reduction_cost.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_fast_rows.patch](reduction_fast_rows.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_final_rows.patch](reduction_final_rows.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_modular.patch](reduction_modular.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_pair.patch](reduction_pair.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_sparse_rows.patch](reduction_sparse_rows.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_build.py](s00_build.py)

The program patches source selection inside native Kira and reuse the responsive shutdown.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / os.getenv('KIRA_RUNTIME_BUILD_DIR', '.tools/kira-integrated-runtime')
BUILD = ROOT / '.tools/kira-build'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

source.read_text()
modified.write_text(t)
(HERE / os.getenv('KIRA_COST_BUILD_RECORD', 'build.json')).write_text(json.dumps(record, indent=2) + '\n')
(BUILD / 'compile_commands.json').read_text()
(ROOT / 'Kira_comparison/acceleration/build.json').read_text()
(ROOT / 'Kira_comparison/fast_expression/build.json').read_text()
p.read_bytes()

```

[s01_build.sh](s01_build.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimeBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py

```

[s02_run.py](s02_run.py)

The program runs one bounded complete Kira reduction, retaining compact exact evidence.

The module defines these callable interfaces:

```python

def sha(p)
def label(a)
def limits()
def disk(path)
def process_rss(pid)
def parse_export(text)
def run(case, size, policy, output, timeout=300, margin=1, reference=None, weights=None, records=True, archive=True, check_masters=False, force=None, scratch_cap=None, compact=True, ordering=None)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s03_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s03_records.py](s03_records.py)

The program shares scientific evidence with atomic writes and a storage bound.

The module defines these callable interfaces:

```python

def payload(value)
def retained()
def put(path, data)
def write_record(path, record)
def read_record(path)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()

```

[s04_pilot.py](s04_pilot.py)

The program checks exact bounded back substitution and unchanged learned policies.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

[s05_pilot.sh](s05_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimePilot
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s04_pilot.py

```

[s06_build_modular.sh](s06_build_modular.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraModularBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
g++ -std=c++17 -O2 ML_model_reduction/runtime_training/s03_test_features.cpp -o .tools/kira-runtime-modular/feature_test
.tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s04_test_features.py
export KIRA_RUNTIME_HEADER=s02_modular_policy.h KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-modular
export KIRA_COST_BUILD_RECORD=modular_build.json KIRA_COST_PATCH=reduction_modular.patch
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py

```

[s07_collect.py](s07_collect.py)

The program collects exact local symbolic costs across ordinary and deeper target batches.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_run`, `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

path.write_text(json.dumps(results, indent=2) + '\n')
(HERE / 'families.json').read_text()
(ROOT / 'ML_model_reduction/runtime_training/feature_tests.json').read_text()

```

[s08_collect.sh](s08_collect.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimeLabels
#$ -t 1-9
#$ -tc 2
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s07_collect.py

```

[s09_train.sh](s09_train.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimeFit
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s05_train.py

```

[s100_plot_shared.py](s100_plot_shared.py)

The program plots complete times relative to the preceding implementation and native control.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'fast_evaluation/confirmation_summary.json').read_text()

```

[s101_build_shared_report.sh](s101_build_shared_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s100_plot_shared.py
make -C report all

```

[s102_finalize_shared.sh](s102_finalize_shared.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedAudit
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s92_summarize_shared.py confirmation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s98_check_shared_application.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s95_audit_shared.py

```

[s103_document_shared_readmes.py](s103_document_shared_readmes.py)

The program updates the current integration guide while preserving previous experiment records.

The module defines these callable interfaces:

```python

def replace_block(path, marker, text)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(old + '\n' + marker + '\n' + text + '\n')
(EXP / 'README.md').write_text(text)
(EXP / 'release.json').write_text(json.dumps(release, indent=2) + '\n')
(EXP / 'confirmation_summary.json').read_text()
(EXP / 'verification.json').read_text()
(EXP / 'application_verification.json').read_text()
p.read_bytes()

```

[s104_prepare_shared_report.sh](s104_prepare_shared_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedReport
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import ast,hashlib,json,pathlib,subprocess,sys,xml.etree.ElementTree as ET
root=pathlib.Path.cwd();here=root/"Kira_comparison/integrated_runtime";exp=here/"fast_evaluation"
sys.path.insert(0,str(here))
from s93_freeze_shared import verify
from s03_records import retained
verify()
assert json.loads((exp/"verification.json").read_text())["all_passed"]
assert json.loads((exp/"confirmation_summary.json").read_text())["observed"]==800
assert json.loads((exp/"application_verification.json").read_text())["checks"]==8
active={n.findtext("JB_job_number") for n in ET.fromstring(subprocess.check_output(['/u/systems/UGE8.6.4/bin/lx-amd64/qstat', '-xml', '-u', 'rushil'])).iter("job_list")}
assert not active & {"15120808","15120815","15120819","15120827","15120864"}
assert retained()<32*1024**2
assert sum(p.stat().st_blocks*512 for p in (root/".tools/kira-shared-inference").rglob("*") if p.is_file())<16*1024**2
for parent in [here,root/"ML_model_seed_selection/runtime_inference",root/"ML_model_reduction/runtime_training"]:
 for p in parent.glob("*.py"):ast.parse(p.read_text())
 for p in parent.glob("*.sh"):subprocess.run(["bash","-n",str(p)],check=True)
state=root/".tools/kira-shared-publication/completion.json"
assert not state.exists()
state.write_text(json.dumps(dict(stage="comparisons_validated",all_declared_jobs_finished=True,published_blob_upper_bytes=44470272),indent=2)+"\n")
print("Final checks and resource limits verified",flush=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s103_document_shared_readmes.py
.tools/seed-model/venv/bin/python .tools/kira-shared-publication/s00_publish.py data
.tools/seed-model/venv/bin/python - <<'PY'
import json,subprocess
s=json.load(open(".tools/kira-shared-publication/completion.json"))
subprocess.run([".tools/seed-model/venv/bin/python","Kira_comparison/integrated_runtime/s99_document_shared.py","--data-commit",s["data_commit"]],check=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s100_plot_shared.py
make -C report all

```

[s105_parallel_records.py](s105_parallel_records.py)

The program bounds new evidence separately and reuse unchanged immutable field blobs.

The module defines these callable interfaces:

```python

def retained()
def put(path, data)
def field_path(digest)
def write_record(path, record)
def read_record(path)

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(EXP / 'resource_plan.json').read_text()

```

[s106_run_parallel.py](s106_run_parallel.py)

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

The imported project modules are `s07_seed`, `s105_parallel_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s107_workflow_parallel.py](s107_workflow_parallel.py)

The program runs a complete fixed fallback policy; all production costs are retained.

The module defines these callable interfaces:

```python

def workflow(case, size, variant, reference, output, basis=None)
def main()

```

The imported project modules are `s105_parallel_records`, `s106_run_parallel`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; required=True.
- `'--variant'`: required=True.
- `'--reference'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s108_reduce.py](s108_reduce.py)

The program reduces new targets with a known master basis; reference answers are optional.

The module defines these callable interfaces:

```python

def select(case, size, requested)
def main()

```

The imported project modules are `s105_parallel_records`, `s107_workflow_parallel`, `s10_fit_thresholds`, `s113_freeze_parallel`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--masters-file'`: type=pathlib.Path; help='JSON list of master index vectors; target coefficients are not required'.
- `'--reference'`: type=pathlib.Path; help='Optional exact-reference mode used for benchmarks'.
- `'--output'`: type=pathlib.Path; required=True.
- `'--policy'`: choices=['auto', 'native', 'seed', 'row', 'both']; default='auto'.
- `'--verify-release'`: action='store_true'; help='Run the common release-integrity check before timing'.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').read_text()
a.family_file.read_text()
a.masters_file.read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/threshold_policy.json').read_text()

```

[s109_build_parallel.sh](s109_build_parallel.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
mkdir -p .tools/kira-parallel-inference
g++ -std=c++17 -O3 -ffp-contract=off -fopt-info-vec-optimized=.tools/kira-parallel-inference/vectorization.log -fPIC -shared -static-libstdc++ -static-libgcc -Wl,--exclude-libs,ALL ML_model_seed_selection/runtime_inference/s13_lane_runtime.cpp -o .tools/kira-parallel-inference/libseed.so
g++ -std=c++17 -O2 -I ML_model_reduction/runtime_training Kira_comparison/parallel_inference/s00_check_arithmetic.cpp -o .tools/kira-parallel-inference/check_arithmetic
.tools/kira-parallel-inference/check_arithmetic | tee Kira_comparison/parallel_inference/arithmetic_check.json
.tools/seed-model/venv/bin/python Kira_comparison/parallel_inference/s01_check_seed.py
KIRA_RUNTIME_BUILD_DIR=.tools/kira-parallel-inference KIRA_RUNTIME_HEADER=s20_literal_policy.h KIRA_COST_BUILD_RECORD=../parallel_inference/build.json KIRA_COST_PATCH=../parallel_inference/reduction_parallel.patch python3 Kira_comparison/integrated_runtime/s00_build.py

```

[s10_verify_seed.sh](s10_verify_seed.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedVector
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s01_verify.py

```

[s110_compare_parallel.py](s110_compare_parallel.py)

The program compares old and shared inference with fixed weights and exact native reductions.

The module defines these callable interfaces:

```python

def parity(a, b)
def main()

```

The imported project modules are `s105_parallel_records`, `s113_freeze_parallel`, `s81_reduce`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

The command accepts these parser options:

- `'phase'`: choices=['validation', 'confirmation'].

These calls show the stored input and output interface:

```python

(EXP / 'freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()
(HERE / 'families.json').read_text()

```

[s111_validate_parallel.sh](s111_validate_parallel.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s110_compare_parallel.py validation

```

[s112_summarize_parallel.py](s112_summarize_parallel.py)

The program retains all matched complete costs and independently assert unchanged decisions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s105_parallel_records`, `s110_compare_parallel`, `s76_summarize_pair_reserved`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

The command accepts these parser options:

- `'phase'`: choices=['validation', 'confirmation'].

These calls show the stored input and output interface:

```python

(EXP / (a.phase + '_summary.json')).write_text(json.dumps(result, indent=2) + '\n')
(EXP / 'freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()
(HERE / 'families.json').read_text()

```

[s113_freeze_parallel.py](s113_freeze_parallel.py)

The program freezes exact arithmetic changes before the repeated implementation comparison.

The module defines these callable interfaces:

```python

def sha(p)
def verify()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(EXP / 'freeze.json').write_text(json.dumps(f, indent=2) + '\n')
(EXP / 'freeze.json').read_text()
(EXP / 'validation_summary.json').read_text()
(EXP / 'arithmetic_check.json').read_text()
(EXP / 'seed_parity.json').read_text()
p.read_bytes()

```

[s114_confirm_parallel.sh](s114_confirm_parallel.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelTest
#$ -t 1-8
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s110_compare_parallel.py confirmation

```

[s115_audit_parallel.py](s115_audit_parallel.py)

The program checks new exact coefficients, timing accounting and native model use.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s105_parallel_records`, `s113_freeze_parallel`, `s30_verify`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(EXP / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s116_finalize_parallel.sh](s116_finalize_parallel.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelAudit
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s112_summarize_parallel.py confirmation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s117_check_parallel_application.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s115_audit_parallel.py

```

[s117_check_parallel_application.py](s117_check_parallel_application.py)

The program checks real basis-only reductions against reference answers after execution.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s105_parallel_records`, `s113_freeze_parallel`, `s30_verify`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'Kira_comparison/parallel_inference/application_verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'reserved_families.json').read_text()
casefile.write_text(json.dumps(case, sort_keys=True) + '\n')
masterfile.write_text(json.dumps(reference['masters']) + '\n')
p.read_bytes()

```

[s118_freeze_parallel.sh](s118_freeze_parallel.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelFreeze
#$ -l h_rt=00:20:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s112_summarize_parallel.py validation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s113_freeze_parallel.py

```

[s119_document_parallel.py](s119_document_parallel.py)

The program writes the mathematical changes and measured complete costs from verified data.

The module defines these callable interfaces:

```python

def num(x)
def interval(d)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_parallel_inference.tex').write_text(text)
p.read_text()
p.write_text(main)
p.write_text(s)
(EXP / 'confirmation_summary.json').read_text()
(EXP / 'verification.json').read_text()
(EXP / 'application_verification.json').read_text()
(EXP / 'seed_parity.json').read_text()
(EXP / 'arithmetic_check.json').read_text()
(EXP / 'confirmation_summary.json').read_bytes()

```

[s11_scratch_pilot.py](s11_scratch_pilot.py)

The program measures project and node scratch with exact, matched native reductions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(out / 'environment.json').write_text(json.dumps(info, indent=2) + '\n')

```

[s120_plot_parallel.py](s120_plot_parallel.py)

The program plots complete times relative to the preceding implementation and native control.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'Kira_comparison/parallel_inference/confirmation_summary.json').read_text()

```

[s121_build_parallel_report.sh](s121_build_parallel_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s120_plot_parallel.py
make -C report all

```

[s122_document_parallel_readmes.py](s122_document_parallel_readmes.py)

The program documents the current exact implementation and the rejected development candidate.

The module defines these callable interfaces:

```python

def update(p, text)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/parallel_inference'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(s + '\n' + marker + '\n' + text + '\n')
(EXP / 'README.md').write_text(text)
(EXP / 'release.json').write_text(json.dumps(release, indent=2) + '\n')
(EXP / 'confirmation_summary.json').read_text()
(EXP / 'verification.json').read_text()
(EXP / 'application_verification.json').read_text()
p.read_bytes()

```

[s123_prepare_parallel_report.sh](s123_prepare_parallel_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelReport
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import ast,hashlib,json,pathlib,subprocess,sys,xml.etree.ElementTree as ET
root=pathlib.Path.cwd();here=root/"Kira_comparison/integrated_runtime";exp=root/"Kira_comparison/parallel_inference"
sys.path.insert(0,str(here))
from s113_freeze_parallel import verify
from s03_records import retained
verify()
assert json.loads((exp/"verification.json").read_text())["all_passed"]
assert json.loads((exp/"confirmation_summary.json").read_text())["observed"]==640
assert json.loads((exp/"application_verification.json").read_text())["checks"]==8
active={n.findtext("JB_job_number") for n in ET.fromstring(subprocess.check_output(['/u/systems/UGE8.6.4/bin/lx-amd64/qstat', '-xml', '-u', 'rushil'])).iter("job_list")}
jobs=json.loads((root/".tools/kira-parallel-publication/jobs.json").read_text())
assert not active & {v for v in jobs.values() if isinstance(v,str)}
assert retained()<32*1024**2
from s105_parallel_records import retained as new_retained
assert new_retained()<12*1024**2
assert sum(p.stat().st_blocks*512 for p in (root/".tools/kira-parallel-inference").rglob("*") if p.is_file())<24*1024**2
for parent in [here,root/"ML_model_seed_selection/runtime_inference",root/"ML_model_reduction/runtime_training"]:
 for p in parent.glob("*.py"):ast.parse(p.read_text())
 for p in parent.glob("*.sh"):subprocess.run(["bash","-n",str(p)],check=True)
state=root/".tools/kira-parallel-publication/completion.json"
assert not state.exists()
state.write_text(json.dumps(dict(stage="comparisons_validated",all_declared_jobs_finished=True,published_blob_upper_bytes=66781184),indent=2)+"\n")
print("Final checks and resource limits verified",flush=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s122_document_parallel_readmes.py
.tools/seed-model/venv/bin/python .tools/kira-parallel-publication/s00_publish.py data
.tools/seed-model/venv/bin/python - <<'PY'
import json,subprocess
s=json.load(open(".tools/kira-parallel-publication/completion.json"))
subprocess.run([".tools/seed-model/venv/bin/python","Kira_comparison/integrated_runtime/s119_document_parallel.py","--data-commit",s["data_commit"]],check=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s120_plot_parallel.py
make -C report all

```

[s12_scratch_pilot.sh](s12_scratch_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraScratchCost
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s11_scratch_pilot.py

```

[s13_ordering_probe.py](s13_ordering_probe.py)

The program compares the eight supported integral orderings on validation cases.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s14_runtime_config`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s14_runtime_config.py](s14_runtime_config.py)

The program chooses temporary-storage placement from the separate exact native pilot.

The module defines these callable interfaces:

```python

def configuration()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(record, indent=2) + '\n')
p.read_text()
p.read_bytes()

```

[s15_ordering_probe.sh](s15_ordering_probe.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraOrderProbe
#$ -l h_rt=02:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s13_ordering_probe.py

```

[s16_validate_rows.py](s16_validate_rows.py)

The program tests repeated row decisions in fresh native reductions on validation cases.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s14_runtime_config`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(ROOT / 'ML_model_reduction/runtime_training/training_results.json').read_text()

```

[s17_validate_rows.sh](s17_validate_rows.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimeRows
#$ -l h_rt=06:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s16_validate_rows.py

```

[s18_build_fast_rows.sh](s18_build_fast_rows.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFastRowsBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_RUNTIME_HEADER=s07_fast_policy.h KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-fast
export KIRA_COST_BUILD_RECORD=fast_rows_build.json KIRA_COST_PATCH=reduction_fast_rows.patch
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py

```

[s19_verify_fast_rows.py](s19_verify_fast_rows.py)

The program verifies shared feature formulas and native tree scores in exact reductions.

The module defines these callable interfaces:

```python

def score(nodes, x)
def main()

```

The imported project modules are `s02_run`, `s03_records`, `s14_runtime_config`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'fast_row_parity.json').write_text(json.dumps(result, indent=2) + '\n')
(folder / 'model.json').read_text()
(HERE / 'families.json').read_text()

```

[s20_verify_fast_rows.sh](s20_verify_fast_rows.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFastRowCheck
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s19_verify_fast_rows.py

```

[s21_trajectory_search.py](s21_trajectory_search.py)

The program measures complete native trajectories for a bounded learned cost-policy search.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s14_runtime_config`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(folder / 'trajectory_candidates.json').read_text()

```

[s22_trajectory_search.sh](s22_trajectory_search.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTrajectory
#$ -t 1-6
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s21_trajectory_search.py

```

[s23_validate_trajectories.py](s23_validate_trajectories.py)

The program measures learned trajectory policies and seed integration on development validation.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s14_runtime_config`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(folder / 'trajectory_selection.json').read_text()
(HERE / 'families.json').read_text()

```

[s24_workflow.py](s24_workflow.py)

The program runs a complete fixed fallback policy; all production costs are retained.

The module defines these callable interfaces:

```python

def workflow(case, size, variant, reference, output)
def main()

```

The imported project modules are `s02_run`, `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; required=True.
- `'--variant'`: required=True.
- `'--reference'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s25_select_trajectory.sh](s25_select_trajectory.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTrajectoryFit
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 1572864
.tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s09_select_trajectory.py

```

[s26_validate_trajectories.sh](s26_validate_trajectories.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTrajectoryVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s23_validate_trajectories.py

```

[s27_build_ephemeral_db.py](s27_build_ephemeral_db.py)

The program builds opt-in database settings restricted to disposable trial directories.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / '.tools/kira-runtime-db'
BUILD = ROOT / '.tools/kira-build'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

source.read_text()
target.write_text(s)
(HERE / 'ephemeral_database.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True), s.splitlines(True), fromfile='a/src/kira/dataBase.cpp', tofile='b/src/kira/dataBase.cpp')))
(BUILD / 'compile_commands.json').read_text()
(HERE / 'fast_rows_build.json').read_text()
p.read_bytes()

```

[s28_build_ephemeral_db.sh](s28_build_ephemeral_db.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTempDBBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s27_build_ephemeral_db.py

```

[s29_ephemeral_pilot.py](s29_ephemeral_pilot.py)

The file provides counterbalanced exact comparison of disposable database settings.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s30_verify.py](s30_verify.py)

The program checks all retained exact exports and complete workflow accounting.

The module defines these callable interfaces:

```python

def seed_candidates(case_id, r, s, d)
def check_integration(record, counts)
def main()

```

The imported project modules are `s03_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'reserved_families.json').read_text()
(HERE / 'deployment.json').read_text()
(HERE / 'freeze.json').read_text()
(HERE / 'pair_freeze.json').read_text()
weights.read_bytes()
(ROOT / name).read_bytes()

```

[s31_development_summary.py](s31_development_summary.py)

The program summarizes complete trajectory validation without using reserved measurements.

The module defines these callable interfaces:

```python

def geo(x)
def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'development_summary.json').write_text(json.dumps(result, indent=2) + '\n')
(folder / 'trajectory_selection.json').read_text()
(HERE / 'families.json').read_text()
p.read_bytes()

```

[s32_test_database_guard.py](s32_test_database_guard.py)

The program verifies disposable-directory guards against actual compiled database helper.

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

(out / 'dataBase.cpp').read_text()
cpp.write_text(harness)
(HERE / 'database_guard_tests.json').write_text(json.dumps(record, indent=2) + '\n')

```

[s33_test_database_guard.sh](s33_test_database_guard.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTempDBCheck
#$ -l h_rt=00:05:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 1572864
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s32_test_database_guard.py

```

[s34_reserved_families.py](s34_reserved_families.py)

The program defines fresh physical test profiles before inspecting any reserved reductions.

The module defines these callable interfaces:

```python

def deeper(d)
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

dest.write_text(json.dumps(result, indent=2) + '\n')
(ROOT / 'Kira_comparison/multiloop_native/families.json').read_text()
dest.read_bytes()

```

[s35_profile_preparation.py](s35_profile_preparation.py)

The program profiles preparation on one validation case without using the timing as a benchmark.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s02_run`, `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
(HERE / 'families.json').read_text()

```

[s36_build_sparse_rows.py](s36_build_sparse_rows.py)

The program specializes feature construction for the fitted sparse linear row policies.

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

(folder / 's07_fast_policy.h').read_text()
(folder / 's10_sparse_policy.h').write_text(s)

```

[s37_build_sparse_rows.sh](s37_build_sparse_rows.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSparseRowsBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s36_build_sparse_rows.py
KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-sparse KIRA_RUNTIME_HEADER=s10_sparse_policy.h KIRA_COST_BUILD_RECORD=sparse_rows_build.json KIRA_COST_PATCH=reduction_sparse_rows.patch python3 Kira_comparison/integrated_runtime/s00_build.py

```

[s38_validate_sparse_rows.py](s38_validate_sparse_rows.py)

The program verifies sparse feature decisions and measure the selected policies with shared controls.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'ML_model_reduction/runtime_training/trajectory_selection.json').read_text()
(HERE / 'families.json').read_text()

```

[s39_validate_sparse_rows.sh](s39_validate_sparse_rows.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSparseRowsVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s38_validate_sparse_rows.py

```

[s40_seed_threshold_search.py](s40_seed_threshold_search.py)

The program fits seed thresholds from complete training workflows, retaining failed attempts.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()

```

[s41_seed_threshold_search.sh](s41_seed_threshold_search.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedCostFit
#$ -t 1-6
#$ -tc 2
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s40_seed_threshold_search.py

```

[s42_fit_seed_thresholds.sh](s42_fit_seed_thresholds.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedThreshold
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 1572864
python3 ML_model_seed_selection/runtime_inference/s10_fit_thresholds.py

```

[s43_finalize_controls.py](s43_finalize_controls.py)

The program applies model-free controls and the same needed-feature optimization to all row policies.

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

(model / 's10_sparse_policy.h').read_text()
(model / 's11_final_policy.h').write_text(s)
p.read_text()
p.write_text(s)

```

[s44_build_final.sh](s44_build_final.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFinalRowsBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s43_finalize_controls.py
KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-final KIRA_RUNTIME_HEADER=s11_final_policy.h KIRA_COST_BUILD_RECORD=final_rows_build.json KIRA_COST_PATCH=reduction_final_rows.patch python3 Kira_comparison/integrated_runtime/s00_build.py

```

[s45_validate_integrated.py](s45_validate_integrated.py)

The program validates fitted thresholds and row policies against the smaller native control.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(folder / 'threshold_policy.json').read_text()
(folder / 'compiled_threshold_parity.json').read_text()
(folder / 'cold_benchmark.json').read_text()

```

[s46_validate_integrated.sh](s46_validate_integrated.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraIntegratedVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s45_validate_integrated.py

```

[s47_basis_admission.py](s47_basis_admission.py)

The program rejects exports with unresolved integrals before coefficient comparison.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

p.read_text()
p.write_text(s)

```

[s48_freeze_integrated.py](s48_freeze_integrated.py)

The program selects on validation and freeze before any new reserved reduction.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').write_text(json.dumps(config, indent=2) + '\n')
(HERE / 'integrated_validation_summary.json').write_text(json.dumps(dict(complete=len(rows), cases=data, selection=config), indent=2) + '\n')
(HERE / 'freeze.json').write_text(json.dumps(protocol, indent=2) + '\n')
p.read_bytes()
(HERE / 'families.json').read_text()

```

[s49_reserved_references.py](s49_reserved_references.py)

The program prepares common native master bases sequentially under the reference budget.

The module defines these callable interfaces:

```python

def verify()
def main()

```

The imported project modules are `s02_run`, `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()
(ROOT / n).read_bytes()

```

[s50_reserved_references.sh](s50_reserved_references.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFinalRefs

#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s49_reserved_references.py

```

[s51_reserved_test.py](s51_reserved_test.py)

The program runs frozen, counterbalanced full-workflow ablations on new physical profiles.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`, `s24_workflow`, `s49_reserved_references`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'reserved_families.json').read_text()
(HERE / 'deployment.json').read_text()
(ROOT / frozen['seed_thresholds']).read_text()

```

[s52_reserved_test.sh](s52_reserved_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFinalTest
#$ -t 1-8
#$ -tc 2
#$ -l h_rt=04:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s51_reserved_test.py

```

[s53_summarize_reserved.py](s53_summarize_reserved.py)

The program summarizes every frozen trial, preserving failures and grouped paired timing.

The module defines these callable interfaces:

```python

def gm(xs)
def compare(data, a, b, field)
def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s54_plot_reserved.py](s54_plot_reserved.py)

The program renders exact paired complete-time and operation comparisons.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').read_text()

```

[s55_freeze_and_references.sh](s55_freeze_and_references.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFreezeRefs
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s48_freeze_integrated.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s49_reserved_references.py

```

[s56_reduce.py](s56_reduce.py)

The program applies the frozen integrated policy to a complete physical-family batch.

The module defines these callable interfaces:

```python

def select(case, size, requested)
def main()

```

The imported project modules are `s10_fit_thresholds`, `s24_workflow`, `s49_reserved_references`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True; help='One case object with definition, targets, id, group and topology_group'.
- `'--size'`: type=int; required=True.
- `'--reference'`: type=pathlib.Path; required=True; help='Exact common master-basis reduction record'.
- `'--output'`: type=pathlib.Path; required=True.
- `'--policy'`: choices=['auto', 'native', 'seed', 'row', 'both']; default='auto'.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').read_text()
a.family_file.read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/threshold_policy.json').read_text()

```

[s57_document.py](s57_document.py)

The program writes the scientific report from frozen exact-test summaries.

The module defines these callable interfaces:

```python

def num(x)
def interval(x)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_integrated_results.tex').write_text(text)
p.read_text()
p.write_text(main)
p.write_text(s)
(HERE / 'report_values.json').write_text(json.dumps(values, indent=2) + '\n')
(HERE / 'summary.json').read_text()
(HERE / 'verification.json').read_text()
(HERE / 'summary.json').read_bytes()

```

[s58_build_report.sh](s58_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimeReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s54_plot_reserved.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s85_plot_pair.py
make -C report all

```

[s59_audit.sh](s59_audit.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRuntimeAudit
#$ -l h_rt=01:00:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s53_summarize_reserved.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s66_summarize_cache.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s30_verify.py

```

[s60_document_readmes.py](s60_document_readmes.py)

The program maintains the integration and model guides from the retained run state.

The module defines these callable interfaces:

```python

def catalog(folder)
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

(HERE / 'README.md').write_text(text)
(HERE / 'summary.json').read_text()
(HERE / 'pair_reserved_summary.json').read_text()
p.read_text()
p.write_text(s)

```

[s61_run_cached.py](s61_run_cached.py)

The program runs one bounded complete Kira reduction, retaining compact exact evidence.

The module defines these callable interfaces:

```python

def sha(p)
def label(a)
def limits()
def disk(path)
def process_rss(pid)
def parse_export(text)
def run(case, size, policy, output, timeout=300, margin=1, reference=None, weights=None, records=True, archive=True, check_masters=False, force=None, scratch_cap=None, compact=True, ordering=None)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s03_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s62_workflow_cached.py](s62_workflow_cached.py)

The program runs a complete fixed fallback policy; all production costs are retained.

The module defines these callable interfaces:

```python

def workflow(case, size, variant, reference, output)
def main()

```

The imported project modules are `s03_records`, `s61_run_cached`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; required=True.
- `'--variant'`: required=True.
- `'--reference'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s63_build_cached.sh](s63_build_cached.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraInverseBuild
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-cached KIRA_RUNTIME_HEADER=s13_cached_policy.h KIRA_COST_BUILD_RECORD=cached_build.json KIRA_COST_PATCH=reduction_cached.patch python3 Kira_comparison/integrated_runtime/s00_build.py

```

[s64_validate_cache.py](s64_validate_cache.py)

The program checks inverse-cache parity and full workflow cost on validation profiles only.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/threshold_policy.json').read_text()
(HERE / 'families.json').read_text()

```

[s65_validate_cache.sh](s65_validate_cache.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraInverseVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s64_validate_cache.py

```

[s66_summarize_cache.py](s66_summarize_cache.py)

The program assesss a numerically identical inverse cache using validation only.

The module defines these callable interfaces:

```python

def gm(xs)
def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'cache_summary.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s67_build_pair.sh](s67_build_pair.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPairBuild
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-pair KIRA_RUNTIME_HEADER=s14_pair_policy.h KIRA_COST_BUILD_RECORD=pair_build.json KIRA_COST_PATCH=reduction_pair.patch python3 Kira_comparison/integrated_runtime/s00_build.py

```

[s68_run_pair.py](s68_run_pair.py)

The program runs one bounded complete Kira reduction, retaining compact exact evidence.

The module defines these callable interfaces:

```python

def sha(p)
def label(a)
def limits()
def disk(path)
def process_rss(pid)
def parse_export(text)
def run(case, size, policy, output, timeout=300, margin=1, reference=None, weights=None, records=True, archive=True, check_masters=False, force=None, scratch_cap=None, compact=True, ordering=None)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s03_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s69_workflow_pair.py](s69_workflow_pair.py)

The program runs a complete fixed fallback policy; all production costs are retained.

The module defines these callable interfaces:

```python

def workflow(case, size, variant, reference, output)
def main()

```

The imported project modules are `s03_records`, `s68_run_pair`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; required=True.
- `'--variant'`: required=True.
- `'--reference'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s70_validate_pair.py](s70_validate_pair.py)

The program checks two-row shortcut parity and full workflow cost on validation profiles only.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/threshold_policy.json').read_text()
(HERE / 'families.json').read_text()

```

[s71_validate_pair.sh](s71_validate_pair.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPairVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s70_validate_pair.py

```

[s72_summarize_pair.py](s72_summarize_pair.py)

The program assesss a numerically identical two-row shortcut using validation only.

The module defines these callable interfaces:

```python

def gm(xs)
def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'pair_summary.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s73_freeze_pair.py](s73_freeze_pair.py)

The program freezes an unchanged-choice row shortcut only after its validation rule passes.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s49_reserved_references`, `s72_summarize_pair`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'pair_freeze.json').write_text(json.dumps(frozen, indent=2) + '\n')
(HERE / 'pair_summary.json').read_text()
(HERE / 'freeze.json').read_bytes()
p.read_bytes()

```

[s74_reserved_pair.py](s74_reserved_pair.py)

The program runs frozen, counterbalanced full-workflow ablations on new physical profiles.

The module defines these callable interfaces:

```python

def verify()
def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`, `s49_reserved_references`, `s69_workflow_pair`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'pair_freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()
(HERE / 'deployment.json').read_text()
(ROOT / frozen['seed_thresholds']).read_text()
(HERE / 'freeze.json').read_bytes()
(ROOT / n).read_bytes()

```

[s75_reserved_pair.sh](s75_reserved_pair.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPairConfirm
#$ -t 1-8
#$ -tc 2
#$ -l h_rt=04:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
if [ -f Kira_comparison/integrated_runtime/pair_freeze.json ]; then
 .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s74_reserved_pair.py
fi

```

[s76_summarize_pair_reserved.py](s76_summarize_pair_reserved.py)

The program summarizes every frozen trial, preserving failures and grouped paired timing.

The module defines these callable interfaces:

```python

def gm(xs)
def compare(data, a, b, field)
def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'pair_reserved_summary.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'pair_freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s77_audit_final.sh](s77_audit_final.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFinalAudit
#$ -l h_rt=01:00:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s53_summarize_reserved.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s66_summarize_cache.py
 .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s72_summarize_pair.py
if [ -f Kira_comparison/integrated_runtime/pair_freeze.json ]; then
 .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s76_summarize_pair_reserved.py
fi
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s30_verify.py

```

[s78_freeze_pair.sh](s78_freeze_pair.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPairFreeze
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 1572864
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s73_freeze_pair.py

```

[s79_run_application.py](s79_run_application.py)

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

The imported project modules are `s03_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s80_workflow_application.py](s80_workflow_application.py)

The program runs a complete fixed fallback policy; all production costs are retained.

The module defines these callable interfaces:

```python

def workflow(case, size, variant, reference, output, basis=None)
def main()

```

The imported project modules are `s03_records`, `s79_run_application`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; required=True.
- `'--variant'`: required=True.
- `'--reference'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s81_reduce.py](s81_reduce.py)

The program reduces new targets with a known master basis; reference answers are optional.

The module defines these callable interfaces:

```python

def select(case, size, requested)
def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`, `s74_reserved_pair`, `s80_workflow_application`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--masters-file'`: type=pathlib.Path; help='JSON list of master index vectors; target coefficients are not required'.
- `'--reference'`: type=pathlib.Path; help='Optional exact-reference mode used for benchmarks'.
- `'--output'`: type=pathlib.Path; required=True.
- `'--policy'`: choices=['auto', 'native', 'seed', 'row', 'both']; default='auto'.
- `'--verify-release'`: action='store_true'; help='Run the common release-integrity check before timing'.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').read_text()
a.family_file.read_text()
a.masters_file.read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/threshold_policy.json').read_text()

```

[s82_check_application.py](s82_check_application.py)

The program checks real basis-only reductions against reference answers after execution.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s30_verify`, `s74_reserved_pair`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'application_verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'reserved_families.json').read_text()
casefile.write_text(json.dumps(case, sort_keys=True) + '\n')
masterfile.write_text(json.dumps(reference['masters']) + '\n')
p.read_bytes()

```

[s83_check_application.sh](s83_check_application.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraApplication
#$ -l h_rt=00:20:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s82_check_application.py

```

[s84_document_pair.py](s84_document_pair.py)

The program documents the unchanged-choice shortcut and the usable basis-only interface.

The module defines these callable interfaces:

```python

def number(x)
def interval(x)
def evidence(x)
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

(ROOT / 'report/kira_integrated_pair.tex').write_text(text)
p.read_text()
p.write_text(main)
p.write_text(x)
(HERE / 'pair_report_values.json').write_text(json.dumps(dict(confirmation=s, validation=v, application=app, audit=audit), indent=2) + '\n')
(HERE / 'summary.json').read_text()
(HERE / 'pair_reserved_summary.json').read_text()
(HERE / 'pair_summary.json').read_text()
(HERE / 'cache_summary.json').read_text()
(HERE / 'application_verification.json').read_text()
(HERE / 'verification.json').read_text()

```

[s85_plot_pair.py](s85_plot_pair.py)

The program plots complete and forward-stage costs after the two-row shortcut.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'pair_reserved_summary.json').read_text()

```

[s86_run_shared.py](s86_run_shared.py)

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

The imported project modules are `s03_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s87_workflow_shared.py](s87_workflow_shared.py)

The program runs a complete fixed fallback policy; all production costs are retained.

The module defines these callable interfaces:

```python

def workflow(case, size, variant, reference, output, basis=None)
def main()

```

The imported project modules are `s03_records`, `s86_run_shared`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; required=True.
- `'--variant'`: required=True.
- `'--reference'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'families.json').read_text()
(HERE / 'reserved_families.json').read_text()

```

[s88_reduce.py](s88_reduce.py)

The program reduces new targets with a known master basis; reference answers are optional.

The module defines these callable interfaces:

```python

def select(case, size, requested)
def main()

```

The imported project modules are `s03_records`, `s10_fit_thresholds`, `s87_workflow_shared`, `s93_freeze_shared`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--family-file'`: type=pathlib.Path; required=True.
- `'--size'`: type=int; required=True.
- `'--masters-file'`: type=pathlib.Path; help='JSON list of master index vectors; target coefficients are not required'.
- `'--reference'`: type=pathlib.Path; help='Optional exact-reference mode used for benchmarks'.
- `'--output'`: type=pathlib.Path; required=True.
- `'--policy'`: choices=['auto', 'native', 'seed', 'row', 'both']; default='auto'.
- `'--verify-release'`: action='store_true'; help='Run the common release-integrity check before timing'.

These calls show the stored input and output interface:

```python

(HERE / 'deployment.json').read_text()
a.family_file.read_text()
a.masters_file.read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/threshold_policy.json').read_text()

```

[s89_build_shared.sh](s89_build_shared.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedBuild
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
mkdir -p .tools/kira-shared-inference
g++ -std=c++17 -O3 -ffp-contract=off -fPIC -shared -static-libstdc++ -static-libgcc -Wl,--exclude-libs,ALL ML_model_seed_selection/runtime_inference/s11_shared_runtime.cpp -o .tools/kira-shared-inference/libseed.so
g++ -std=c++17 -O2 -I ML_model_reduction/runtime_training Kira_comparison/integrated_runtime/fast_evaluation/s00_check_pairs.cpp -o .tools/kira-shared-inference/check_pairs | tee Kira_comparison/integrated_runtime/fast_evaluation/row_feature_check.json
.tools/kira-shared-inference/check_pairs | tee Kira_comparison/integrated_runtime/fast_evaluation/row_feature_check.json
KIRA_RUNTIME_BUILD_DIR=.tools/kira-shared-inference KIRA_RUNTIME_HEADER=s16_shared_policy.h KIRA_COST_BUILD_RECORD=fast_evaluation/build.json KIRA_COST_PATCH=fast_evaluation/reduction_shared.patch python3 Kira_comparison/integrated_runtime/s00_build.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/fast_evaluation/s01_check_seed.py

```

[s90_compare_shared.py](s90_compare_shared.py)

The program compares old and shared inference with fixed weights and exact native reductions.

The module defines these callable interfaces:

```python

def parity(a, b)
def main()

```

The imported project modules are `s03_records`, `s81_reduce`, `s93_freeze_shared`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

The command accepts these parser options:

- `'phase'`: choices=['validation', 'confirmation'].

These calls show the stored input and output interface:

```python

(EXP / 'freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()
(HERE / 'families.json').read_text()

```

[s91_validate_shared.sh](s91_validate_shared.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedVal
#$ -t 1-3
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s90_compare_shared.py validation

```

[s92_summarize_shared.py](s92_summarize_shared.py)

The program retains all matched complete costs and independently assert unchanged decisions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s76_summarize_pair_reserved`, `s90_compare_shared`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

The command accepts these parser options:

- `'phase'`: choices=['validation', 'confirmation'].

These calls show the stored input and output interface:

```python

(EXP / (a.phase + '_summary.json')).write_text(json.dumps(result, indent=2) + '\n')
(EXP / 'freeze.json').read_text()
(HERE / 'reserved_families.json').read_text()
(HERE / 'families.json').read_text()

```

[s93_freeze_shared.py](s93_freeze_shared.py)

The program freezes implementation-only changes after exact and timing validation.

The module defines these callable interfaces:

```python

def sha(p)
def verify()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(EXP / 'freeze.json').write_text(json.dumps(f, indent=2) + '\n')
(EXP / 'freeze.json').read_text()
(EXP / 'validation_summary.json').read_text()
(EXP / 'row_feature_check.json').read_text()
p.read_bytes()
(EXP / 'seed_parity.json').read_text()

```

[s94_confirm_shared.sh](s94_confirm_shared.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedTest
#$ -t 1-8
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s90_compare_shared.py confirmation

```

[s95_audit_shared.py](s95_audit_shared.py)

The program checks new exact coefficients, timing accounting and native model use.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s30_verify`, `s93_freeze_shared`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(EXP / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')

```

[s96_finalize_shared.sh](s96_finalize_shared.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedAudit
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s92_summarize_shared.py confirmation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s98_check_shared_application.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s95_audit_shared.py

```

[s97_freeze_shared.sh](s97_freeze_shared.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedFreeze
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 1572864
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s92_summarize_shared.py validation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s93_freeze_shared.py

```

[s98_check_shared_application.py](s98_check_shared_application.py)

The program checks real basis-only reductions against reference answers after execution.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s30_verify`, `s93_freeze_shared`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'fast_evaluation/application_verification.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'reserved_families.json').read_text()
casefile.write_text(json.dumps(case, sort_keys=True) + '\n')
masterfile.write_text(json.dumps(reference['masters']) + '\n')
p.read_bytes()

```

[s99_document_shared.py](s99_document_shared.py)

The program explains shared neural and row calculations using the completed comparisons.

The module defines these callable interfaces:

```python

def n(x)
def interval(x)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_shared_evaluation.tex').write_text(text)
p.write_text(main)
p.read_text()
p.write_text(t)
(EXP / 'confirmation_summary.json').read_text()
(EXP / 'validation_summary.json').read_text()
(EXP / 'verification.json').read_text()
(EXP / 'application_verification.json').read_text()
(EXP / 'seed_parity.json').read_text()
(EXP / 'confirmation_summary.json').read_bytes()

```

## Data and supporting files

- [application_verification.json](application_verification.json): This file records checks of the corresponding calculation.

- [basis_admission_fix.json](basis_admission_fix.json): This file contains structured records from the parent calculation.

- [build.json](build.json): This file contains structured records from the parent calculation.

- [cache_protocol.json](cache_protocol.json): This file contains structured records from the parent calculation.

- [cache_resource_plan.json](cache_resource_plan.json): This file contains structured records from the parent calculation.

- [cache_summary.json](cache_summary.json): This file contains structured records from the parent calculation.

- [cached_build.json](cached_build.json): This file contains structured records from the parent calculation.

- [database_guard_tests.json](database_guard_tests.json): This file contains structured records from the parent calculation.

- [deployment.json](deployment.json): This file contains structured records from the parent calculation.

- [development_summary.json](development_summary.json): This file contains structured records from the parent calculation.

- [ephemeral_db_build.json](ephemeral_db_build.json): This file contains structured records from the parent calculation.

- [families.json](families.json): This file defines the families in this collection.

- [fast_row_parity.json](fast_row_parity.json): This file contains structured records from the parent calculation.

- [fast_rows_build.json](fast_rows_build.json): This file contains structured records from the parent calculation.

- [final_rows_build.json](final_rows_build.json): This file contains structured records from the parent calculation.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [integrated_validation_summary.json](integrated_validation_summary.json): This file contains structured records from the parent calculation.

- [modular_build.json](modular_build.json): This file contains structured records from the parent calculation.

- [pair_build.json](pair_build.json): This file contains structured records from the parent calculation.

- [pair_freeze.json](pair_freeze.json): This file contains structured records from the parent calculation.

- [pair_protocol.json](pair_protocol.json): This file contains structured records from the parent calculation.

- [pair_report_values.json](pair_report_values.json): This file contains structured records from the parent calculation.

- [pair_reserved_summary.json](pair_reserved_summary.json): This file contains structured records from the parent calculation.

- [pair_summary.json](pair_summary.json): This file contains structured records from the parent calculation.

- [release.json](release.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [reserved_families.json](reserved_families.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [runtime_config.json](runtime_config.json): This file contains structured records from the parent calculation.

- [sparse_rows_build.json](sparse_rows_build.json): This file contains structured records from the parent calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [application_checks](application_checks/README.md).

- [cached_validation](cached_validation/README.md).

- [collection](collection/README.md).

- [control_parity](control_parity/README.md).

- [database_pilot](database_pilot/README.md).

- [fast_evaluation](fast_evaluation/README.md).

- [fast_row_parity](fast_row_parity/README.md).

- [integrated_validation](integrated_validation/README.md).

- [ordering_validation](ordering_validation/README.md).

- [pair_reserved_test](pair_reserved_test/README.md).

- [pair_validation](pair_validation/README.md).

- [pilot](pilot/README.md).

- [pilot_topological_v2](pilot_topological_v2/README.md).

- [preparation_profile](preparation_profile/README.md).

- [references](references/README.md).

- [rejected_workflows](rejected_workflows/README.md).

- [reserved_references](reserved_references/README.md).

- [reserved_test](reserved_test/README.md).

- [row_validation](row_validation/README.md).

- [scratch_pilot](scratch_pilot/README.md).

- [seed_threshold_training](seed_threshold_training/README.md).

- [shared](shared/README.md).

- [sparse_parity](sparse_parity/README.md).

- [sparse_validation](sparse_validation/README.md).

- [trajectory_training](trajectory_training/README.md).

- [trajectory_validation](trajectory_validation/README.md).

- [workflow_attempts](workflow_attempts/README.md).
