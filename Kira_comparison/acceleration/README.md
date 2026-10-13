# acceleration

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

[s00_prepare.py](s00_prepare.py)

The program freezes development and evaluation families before new timing outcomes.

The module defines these callable interfaces:

```python

def sha(p)
def rank(x)
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
(HERE.parent / 'plan.json').read_text()
out.write_text(json.dumps(plan, indent=2) + '\n')
p.read_bytes()
out.read_text()

```

[s01_fast_seed.py](s01_fast_seed.py)

The file provides numPy inference using the original seed model, public inputs and float32 weights.

The module defines these callable interfaces:

```python

def text_features(text, bins)
def index_features(a, cfg)
class FastSeed

```

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'seed_export.json').read_text()

```

[s02_export_seed.py](s02_export_seed.py)

The program exports frozen seed weights and verify inference using training families only.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s01_common`, `s01_fast_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(ROOT / 'ML_model_seed_selection/trained_model.pt', map_location='cpu', weights_only=False)
np.savez(HERE / 'seed_weights.npz', **{k: v.numpy() for k, v in saved['model'].items()})
(HERE / 'seed_export.json').write_text(json.dumps(dict(config=saved['config'], checkpoint_sha256=sha(ROOT / 'ML_model_seed_selection/trained_model.pt')), indent=2) + '\n')
(HERE / 'seed_export_validation.json').write_text(json.dumps(dict(passed=True, partition='train', cases=record, weights_sha256=sha(HERE / 'seed_weights.npz')), indent=2) + '\n')
(HERE / 'plan.json').read_text()

```

[s03_seed_filter.h](s03_seed_filter.h)

The file provides experimental individual-seed gate for Kira/pyRed; GPL-3.0-or-later.

The required headers are `atomic`, `cstdlib`, `fstream`, `iomanip`, `mutex`, `set`, `stdexcept`, `unordered_set`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s04_build.py](s04_build.py)

The program compiles the seed gate separately and link unchanged Kira objects.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = ROOT / '.tools/kira-build'
OUT = ROOT / '.tools/kira-acceleration'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

source.read_text()
dest.write_text(t)
(HERE / 'build.json').write_text(json.dumps(dict(original_sha256=sha(source), modified_sha256=sha(dest), header_sha256=sha(HERE / 's03_seed_filter.h'), binary_sha256=sha(OUT / 'kira'), compile=compile, link=link), indent=2) + '\n')
p.read_bytes()
(BUILD / 'compile_commands.json').read_text()

```

[s05_setup.sh](s05_setup.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelSetup
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/setup.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s02_export_seed.py
python3 Kira_comparison/acceleration/s04_build.py

```

[s06_worker.py](s06_worker.py)

The file provides one bounded native trial; labels are read only after reduction.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`, `s10_native_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'partition'`: The parser accepts a value..
- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(a.scratch / 'seeds.txt').write_text(''.join(('F[' + ','.join(map(str, s)) + ']\n' for s in sorted(selected))))
(a.scratch / 'cpp_context.txt').write_text('\n'.join(lines) + '\n')
(w / 'forward.jsonl').read_text()

```

[s07_run.py](s07_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's06_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s08_run.sh](s08_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccel
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s07_run.py "$@"

```

[s09_fast_row.py](s09_fast_row.py)

The file provides numPy inference with the unchanged reduction checkpoint.

The module defines these callable interfaces:

```python

class FastRow

```

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'row_export.json').read_text()

```

[s10_export_row.py](s10_export_row.py)

The program exports the frozen row model and check numeric equivalence on bounded feature arrays.

The imported external packages are `numpy`, `torch`.

The imported project modules are `s03_model`, `s09_fast_row`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

torch.load(path, map_location='cpu', weights_only=False)
np.savez(HERE / 'row_weights.npz', **{k: v.detach().numpy() for k, v in saved['model'].items()})
(HERE / 'row_export.json').write_text(json.dumps(dict(config=saved['config'], feature_dim=saved['feature_dim'], checkpoint_sha256=hashlib.sha256(path.read_bytes()).hexdigest()), indent=2) + '\n')
(HERE / 'row_export_validation.json').write_text(json.dumps(dict(scope='Implementation equivalence on seeded feature arrays; physical live-state validation follows in native trials.', records=records), indent=2) + '\n')
path.read_bytes()

```

[s11_row_server.py](s11_row_server.py)

The program scores admissible live Kira row operations with the frozen reduction model.

The module defines these callable interfaces:

```python

def emit(x)
def evaluate(text)
def readrow(n)
def sampled(terms)

```

The imported external packages are `numpy`.

The imported project modules are `s01_state`, `s09_fast_row`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

[s12_export_row.sh](s12_export_row.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraRowExport
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/row_export.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s10_export_row.py

```

[s13_audit.py](s13_audit.py)

The file provides independent modular checks of native exports and exact-update evidence.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s08_verify`, `s38_compact_records`, `s39_records`, `s61_evidence_archive`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--stage'`: default='results'.

[s14_summary.py](s14_summary.py)

The program summarizes all planned records, with separate failed and skipped observations.

The module defines these callable interfaces:

```python

def metric_record(path)
def good(r)
def measurement(r)
def comparison(numerator, denominator, metric)

```

The imported project modules are `s39_records`, `s61_evidence_archive`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
(HERE / 'plan.json').read_text()
(HERE / 'frozen_policy.json').read_text()

```

[s15_array.sh](s15_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelArray
#$ -t 1-6
#$ -tc 2
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
exec bash Kira_comparison/acceleration/s08_run.sh --case "$((SGE_TASK_ID-1))" "$@"

```

[s16_select_seeds.py](s16_select_seeds.py)

The program selects native IBP seeds from public family and target files.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_fast_seed`.

The command accepts these parser options:

- `'--definition'`: type=pathlib.Path; required=True.
- `'--masters'`: type=pathlib.Path; required=True.
- `'--targets'`: type=pathlib.Path; required=True.
- `'--candidates'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; required=True.
- `'--name'`: default='F'.
- `'--threshold'`: type=float.
- `'--input-mode'`: choices=['components', 'expressions']; default=None.
- `'--halo'`: action='store_true'.

These calls show the stored input and output interface:

```python

a.output.write_text(''.join((a.name + '[' + ','.join(map(str, s)) + ']\n' for s in sorted(chosen))))
a.output.with_suffix(a.output.suffix + '.json').write_text(json.dumps(record, indent=2) + '\n')
(pathlib.Path(__file__).resolve().parent / 'frozen_policy.json').read_text()
a.definition.read_text()
a.masters.read_text()
a.candidates.read_text()

```

[s17_update_report.py](s17_update_report.py)

The program writes checked native-acceleration results into the report.

The module defines these callable interfaces:

```python

def read(name)
def c(p, b='trim', m='total_seconds')
def ratio(x)
def num(x)
def st(p)
def cratio(x)

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

(ROOT / 'report/kira_acceleration_results.tex').write_text('\n\n'.join(out) + '\n')
p.read_text()
p.write_text(text)
(HERE / 'report_values.json').write_text(json.dumps(values, indent=2) + '\n')
(HERE / name).read_text()
(HERE / 'summary.json').read_bytes()
(HERE / 'results_validation.json').read_bytes()
(HERE / 'expression_test_summary.json').read_bytes()
(HERE / 'expression_matched_summary.json').read_bytes()

```

[s20_freeze.py](s20_freeze.py)

The program chooses the adapter on validation costs and freeze it before new cost tests.

The module defines these callable interfaces:

```python

def sha(p)
def cost(i, policy)
def score(policy)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'plan.json').read_text()
(HERE / 'validation_protocol.json').read_text()
path.write_text(json.dumps(frozen, indent=2) + '\n')
(HERE / 'cpp_equivalence.json').read_text()
path.read_text()
p.read_bytes()

```

[s21_freeze.sh](s21_freeze.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFreeze
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/freeze.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage validation
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s20_freeze.py
bash Kira_comparison/acceleration/s08_run.sh --case 2 --stage combined_pilot --policies combined
bash Kira_comparison/acceleration/s08_run.sh --case 4 --stage combined_pilot --policies combined
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage combined_pilot
.tools/seed-model/venv/bin/python -c 'import json; x=json.load(open("Kira_comparison/acceleration/combined_pilot_validation.json")); assert x["completed"]==2 and not x["incomplete"]'
submission=$("$SGE_ROOT/bin/lx-amd64/qsub" Kira_comparison/acceleration/s22_test_array.sh)
echo "$submission"
array_job=$(echo "$submission" | awk '{split($3,a,"."); print a[1]}')
"$SGE_ROOT/bin/lx-amd64/qsub" -hold_jid "$array_job" Kira_comparison/acceleration/s32_finalize.sh

```

[s22_test_array.sh](s22_test_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelTest
#$ -t 1-24
#$ -tc 8
#$ -l h_rt=01:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
index=$((SGE_TASK_ID-1))
case_id=$((index/2))
if ((index%2==0)); then batch_size=16; else batch_size=64; fi
exec bash Kira_comparison/acceleration/s08_run.sh --case "$case_id" --sizes "$batch_size" --partition test --stage results --repetitions 5 --policies frozen

```

[s23_cpp_model.h](s23_cpp_model.h)

The file provides native inference for the frozen source-row policy; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `cmath`, `cctype`, `cstdint`, `cstdlib`, `fstream`, `iomanip`, `map`, `set`, `sstream`, `stdexcept`, `string`, `vector`, `s24_row_weights.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s24_export_cpp.py](s24_export_cpp.py)

The program writes exact float32 row weights as C++ constants.

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 's24_row_weights.h').write_text('\n'.join(lines) + '\n')

```

[s24_row_weights.h](s24_row_weights.h)

The file provides frozen trained row weights; exported float32 values.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s25_cpp_live_policy.h](s25_cpp_live_policy.h)

The file provides live symbolic forward-elimination experiment; GPL-3.0-or-later.

The required headers are `chrono`, `cstdio`, `cstdlib`, `fstream`, `map`, `memory`, `algorithm`, `set`, `stdexcept`, `vector`, `spawn.h`, `sys/wait.h`, `unistd.h`, `/u/home/r/rushil/ML_for_Kira_Seeding_Reduction/Kira_comparison/acceleration/s23_cpp_model.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s26_build_cpp.py](s26_build_cpp.py)

The program builds native inference while preserving stock and earlier experimental binaries.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE.parent / 'live_matrix/s01_live_policy.h').read_text()
(HERE / 's25_cpp_live_policy.h').write_text(header)
modified.write_text(text)
(HERE / 'cpp_build.json').write_text(json.dumps(record, indent=2) + '\n')
(HERE / 'build.json').read_text()
original.read_text()
p.read_bytes()

```

[s27_build_cpp.sh](s27_build_cpp.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppBuild
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s24_export_cpp.py
python3 Kira_comparison/acceleration/s26_build_cpp.py

```

[s28_cpp_pilot.sh](s28_cpp_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppPilot
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_pilot.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
bash Kira_comparison/acceleration/s08_run.sh --case 2 --stage cpp_pilot --policies row_cpp_native,row_cpp_audit
bash Kira_comparison/acceleration/s08_run.sh --case 4 --stage cpp_pilot --policies row_cpp_native,row_cpp_audit
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s29_cpp_audit.py

```

[s29_cpp_audit.py](s29_cpp_audit.py)

The program checks native coefficient sampling, features, probabilities and chosen updates.

The module defines these callable interfaces:

```python

def reference64(features)

```

The imported external packages are `numpy`.

The imported project modules are `s01_common`, `s01_state`, `s08_verify`, `s09_fast_row`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--stage'`: default='cpp_pilot'.
- `'--diagnostic'`: action='store_true'.

[s30_cpp_pilot_v2.sh](s30_cpp_pilot_v2.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppPilotV2
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_pilot_v2.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
bash Kira_comparison/acceleration/s08_run.sh --case 2 --stage cpp_pilot_v2 --policies row_cpp_native,row_cpp_audit
bash Kira_comparison/acceleration/s08_run.sh --case 4 --stage cpp_pilot_v2 --policies row_cpp_native,row_cpp_audit
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s29_cpp_audit.py --stage cpp_pilot_v2

```

[s31_plot.py](s31_plot.py)

The program creates exportable plots from completed, matched native comparisons.

The module defines these callable interfaces:

```python

def figure(metrics, titles, name)

```

The imported external packages are `matplotlib`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'summary.json').read_text()

```

[s32_finalize.sh](s32_finalize.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelAudit
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage results
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s14_summary.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s31_plot.py

```

[s33_cpp_pilot_v3.sh](s33_cpp_pilot_v3.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppPilotV3
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_pilot_v3.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
bash Kira_comparison/acceleration/s08_run.sh --case 2 --stage cpp_pilot_v3 --policies row_cpp_native,row_cpp_audit
bash Kira_comparison/acceleration/s08_run.sh --case 4 --stage cpp_pilot_v3 --policies row_cpp_native,row_cpp_audit
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s29_cpp_audit.py --stage cpp_pilot_v3

```

[s34_cpp_check.sh](s34_cpp_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppCheck
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_check.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s29_cpp_audit.py --stage cpp_pilot_v3

```

[s35_document.py](s35_document.py)

The program updates documentation from the complete, independently checked comparison.

The module defines these callable interfaces:

```python

def item(p)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'README.md').write_text(text)
p.read_text()
p.write_text(old)
(HERE / 'summary.json').read_text()
(HERE / 'results_validation.json').read_text()
(HERE / 'frozen_policy.json').read_text()

```

[s36_evidence.py](s36_evidence.py)

The file provides content-addressed solver text: preserve evidence without repeated copies.

The module defines these callable interfaces:

```python

def pack(evidence)
def unpack(evidence)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

[s37_build_report.sh](s37_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelPaper
#$ -l h_rt=00:08:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/report_build.log
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s31_plot.py
if [[ -f Kira_comparison/acceleration/expression_test_summary.json ]]; then
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py
fi
if [[ -f Kira_comparison/acceleration/expression_matched_summary.json ]]; then
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py --matched
fi
make -C report

```

[s38_compact_records.py](s38_compact_records.py)

The program deduplicates archived predictions/checks without changing any measured value.

The module defines these callable interfaces:

```python

def packed(value)
def _compact_completed(min_age=30, stage='results')
def compact_completed(min_age=30, stage='results')

```

The imported project modules are `s39_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--min-age'`: type=int; default=30.
- `'--stage'`: default='results'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(previous, indent=2) + '\n')
p.read_text()
path.read_bytes()

```

[s39_records.py](s39_records.py)

The program restores shared structured results and verify their unchanged logical content.

The module defines these callable interfaces:

```python

def canonical(value)
def restore(value)
def read_record(path)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

[s40_preflight_worker.py](s40_preflight_worker.py)

The file provides native trials with Kira master-basis checking before symbolic elimination.

The module defines these callable interfaces:

```python

def checked_native_selected(*args, **kwargs)
def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`, `s10_native_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'partition'`: The parser accepts a value..
- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(a.scratch / 'seeds.txt').write_text(''.join(('F[' + ','.join(map(str, s)) + ']\n' for s in sorted(selected))))
(a.scratch / 'cpp_context.txt').write_text('\n'.join(lines) + '\n')
(w / 'forward.jsonl').read_text()

```

[s41_preflight_run.py](s41_preflight_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='preflight_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's40_preflight_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s42_preflight_pilot.sh](s42_preflight_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPreflight
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s41_preflight_run.py "$@"

```

[s43_adaptive_worker.py](s43_adaptive_worker.py)

The file provides ranked seed expansion with an early native master-basis check.

The module defines these callable interfaces:

```python

def bounds(seeds)
def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`, `s10_native_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `name`: type=int if name in ('case', 'size') else pathlib.Path if name in ('scratch', 'output') else str.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')
seedfile.write_text(''.join(('F[' + ','.join(map(str, s)) + ']\n' for s in sorted(selected))))
(w / 'run.log').write_text('\n'.join(logs))

```

[s44_adaptive_run.py](s44_adaptive_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='adaptive_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's43_adaptive_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s45_adaptive_pilot.sh](s45_adaptive_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAdaptive
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s44_adaptive_run.py "$@"

```

[s46_adaptive_check.sh](s46_adaptive_check.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAdaptCheck
#$ -l h_rt=00:45:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage adaptive_pilot
.tools/seed-model/venv/bin/python - <<'CHECK'
import json
r=json.load(open('Kira_comparison/acceleration/adaptive_pilot_validation.json'))
assert r['passed'] and r['trials']==4 and r['completed']==4,r
CHECK
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s44_adaptive_run.py --partition train --case 4 --sizes 16 --policies trim_checked,pool_checked,adaptive_ml,adaptive_distance --stage adaptive_pilot
for kira_validation_case in 3 4; do
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s44_adaptive_run.py --partition validation --case "$kira_validation_case" --sizes 16 --policies trim_checked,pool_checked,adaptive_ml,adaptive_distance --stage adaptive_validation
done
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage adaptive_pilot
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage adaptive_validation

```

[s47_residual_worker.py](s47_residual_worker.py)

The file provides residual-driven seed expansion with an early native master-basis check.

The module defines these callable interfaces:

```python

def bounds(seeds)
def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`, `s10_native_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `name`: type=int if name in ('case', 'size') else pathlib.Path if name in ('scratch', 'output') else str.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')
seedfile.write_text(''.join(('F[' + ','.join(map(str, s)) + ']\n' for s in sorted(selected))))
(w / 'run.log').write_text('\n'.join(logs))

```

[s48_residual_run.py](s48_residual_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='residual_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's47_residual_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s49_residual_pilot.sh](s49_residual_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraResidual
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s48_residual_run.py "$@"

```

[s50_development_summary.py](s50_development_summary.py)

The program summarizes every early-admission development trial without claiming a timing test.

The imported project modules are `s39_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'development_summary.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / (stage + '_validation.json')).read_text()

```

[s51_development_audit.sh](s51_development_audit.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraDevAudit
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/development_audit.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
for kira_development_stage in preflight_pilot adaptive_pilot adaptive_validation residual_pilot; do
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage "$kira_development_stage"
done
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s50_development_summary.py

```

[s52_development_report.py](s52_development_report.py)

The program renders the checked, separate early-admission development results.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_adaptive_development.tex').write_text(text)
(HERE / 'development_summary.json').read_text()

```

[s53_transfer_worker.py](s53_transfer_worker.py)

The file provides one bounded native trial; labels are read only after reduction.

The module defines these callable interfaces:

```python

def load_case(case, size)
def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`, `s10_native_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'partition'`: The parser accepts a value..
- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(a.scratch / 'seeds.txt').write_text(''.join(('F[' + ','.join(map(str, s)) + ']\n' for s in sorted(selected))))
(a.scratch / 'cpp_context.txt').write_text('\n'.join(lines) + '\n')
(w / 'forward.jsonl').read_text()

```

[s54_transfer_run.py](s54_transfer_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`, `s38_compact_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'transfer_plan.json').read_bytes()
(HERE / 's53_transfer_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s55_transfer_audit.py](s55_transfer_audit.py)

The file provides independent modular checks of native exports and exact-update evidence.

The module defines these callable interfaces:

```python

def load_case(case, size)
def main()

```

The imported project modules are `s01_common`, `s08_verify`, `s38_compact_records`, `s39_records`, `s61_evidence_archive`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--stage'`: default='transfer_test'.

[s56_transfer_test.sh](s56_transfer_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTransfer
#$ -l h_rt=01:10:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s54_transfer_run.py --partition transfer --case 0 --sizes 16,64 --repetitions 5 --policies trim,pool_filter,ml_lower,row_cpp_native,row_cpp,combined --stage transfer_test
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s55_transfer_audit.py

```

[s57_transfer_summary.py](s57_transfer_summary.py)

The file provides paired timing summary for the fixed two-loop transfer experiment.

The module defines these callable interfaces:

```python

def good(r)
def ci(learned, control)

```

The imported project modules are `s39_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'transfer_summary.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'transfer_plan.json').read_text()
(HERE / 'transfer_test_validation.json').read_text()

```

[s58_transfer_plot.py](s58_transfer_plot.py)

The program plots full-cost paired ratios for the fixed two-loop transfer check.

The imported external packages are `matplotlib`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'transfer_summary.json').read_text()

```

[s59_transfer_report.py](s59_transfer_report.py)

The program renders the completed fixed-policy two-loop transfer comparison.

The module defines these callable interfaces:

```python

def mathnum(n)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_transfer_results.tex').write_text('\n'.join(parts))
p.read_text()
p.write_text(text)
(HERE / 'transfer_summary.json').read_text()
(HERE / 'transfer_test_validation.json').read_text()

```

[s60_finish_transfer.sh](s60_finish_transfer.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTransferDoc
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/transfer_finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s57_transfer_summary.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s58_transfer_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s59_transfer_report.py

```

[s61_evidence_archive.py](s61_evidence_archive.py)

The file provides lossless high-dictionary compression of archived solver evidence.

The module defines these callable interfaces:

```python

def unpack(evidence)
def plain_hash(path, opener)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--min-age'`: type=int; default=30.
- `'--minimum-bytes'`: type=int; default=100000.

These calls show the stored input and output interface:

```python

history.write_text(json.dumps(old, indent=2) + '\n')
history.read_text()

```

[s62_compress_evidence.sh](s62_compress_evidence.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCompress
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/evidence_compression.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
ulimit -v 786432
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s61_evidence_archive.py --min-age 30

```

[s63_maintain_archive.sh](s63_maintain_archive.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraArchive
#$ -l h_rt=01:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/archive_monitor.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
ulimit -v 786432
.tools/seed-model/venv/bin/python - <<'MONITOR'
import pathlib,subprocess,time
h=pathlib.Path('Kira_comparison/acceleration')
for iteration in range(180):
 subprocess.run(['.tools/seed-model/venv/bin/python',str(h/'s61_evidence_archive.py'),'--min-age','10'],check=True)
 if len(list((h/'results').glob('*.json.gz')))==720 and len(list((h/'transfer_test').glob('*.json.gz')))==60:
  subprocess.run(['.tools/seed-model/venv/bin/python',str(h/'s61_evidence_archive.py'),'--min-age','0'],check=True)
  break
 time.sleep(20)
MONITOR

```

[s64_resume_trials.py](s64_resume_trials.py)

The program resumes storage-interrupted frozen trials on each original compute node.

The module defines these callable interfaces:

```python

def submit(argv)
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

old.write_text(json.dumps(record, indent=2) + '\n')
next((HERE / 'transfer_test').glob('environment_*.json')).read_text()
ep.read_text()
ep.read_bytes()

```

[s65_expression_worker.py](s65_expression_worker.py)

The program applies fast seed inference directly to complete stored target expressions.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `name`: type=int if name in ('case', 'size') else pathlib.Path if name in ('scratch', 'output') else str.

[s66_expression_run.py](s66_expression_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='expression_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's65_expression_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s67_expression_pilot.sh](s67_expression_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExpression
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s66_expression_run.py "$@"

```

[s68_expression_audit.py](s68_expression_audit.py)

The program validates supplied-expression seed choices and raw Kira exports.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s08_verify`, `s39_records`, `s61_evidence_archive`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--stage'`: required=True.
- `'--plan'`: default='plan.json'.

[s69_expression_preflight.py](s69_expression_preflight.py)

The program checks the master basis early for fast whole-expression seed selection.

The module defines these callable interfaces:

```python

def early_checked_run(work, plan)
def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `name`: type=int if name in ('case', 'size') else pathlib.Path if name in ('scratch', 'output') else str.

These calls show the stored input and output interface:

```python

(work / 'jobs.yaml').write_text('\n'.join(lines) + '\n')
(work / 'jobs.yaml').read_text()

```

[s70_expression_preflight_run.py](s70_expression_preflight_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='expression_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's69_expression_preflight.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s71_expression_preflight.sh](s71_expression_preflight.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprCheck
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s70_expression_preflight_run.py "$@"

```

[s72_expression_small.sh](s72_expression_small.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprSmall
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s66_expression_run.py --partition train --case 2 --sizes 1,4 --repetitions 3 --policies stored_pool,stored_ml,stored_ml_lower --stage expression_small

```

[s73_expression_policy_worker.py](s73_expression_policy_worker.py)

The program dispatches whole-expression policies while preserving existing workers.

The imported project modules are `s65_expression_worker`, `s69_expression_preflight`.

This entry point uses the paths and options set in its source.

[s74_expression_policy_run.py](s74_expression_policy_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='expression_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's73_expression_policy_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s75_expression_validation.sh](s75_expression_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprValid
#$ -l h_rt=00:35:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s74_expression_policy_run.py --partition validation --case "$((SGE_TASK_ID-1))" --sizes 1,16 --repetitions 1 --policies stored_pool,stored_ml_lower,stored_ml_lower_checked --stage expression_validation

```

[s76_expression_summary.py](s76_expression_summary.py)

The program summarizes whole-expression development and choose a validation interface.

The module defines these callable interfaces:

```python

def read(p)

```

The imported project modules are `s39_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'expression_summary.json').write_text(json.dumps(out, indent=2) + '\n')
p.read_text()
(HERE / (stage + '_validation.json')).read_bytes()

```

[s77_expression_finish.sh](s77_expression_finish.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprAudit
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/expression_finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_pilot
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_thresholds
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_preflight
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_small
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_validation
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s76_expression_summary.py

```

[s78_expression_controls_worker.py](s78_expression_controls_worker.py)

The program compares whole-expression learned seeds with exact Kira and a distance control.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s01_fast_seed`, `s02_worker`, `s69_expression_preflight`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `name`: type=int if name in ('case', 'size') else pathlib.Path if name in ('scratch', 'output') else str.

[s79_expression_test_run.py](s79_expression_test_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='expression_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'expression_freeze.json').read_text()
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's78_expression_controls_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s80_expression_test_audit.py](s80_expression_test_audit.py)

The program validates supplied-expression seed choices and raw Kira exports.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s08_verify`, `s39_records`, `s61_evidence_archive`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--stage'`: required=True.
- `'--plan'`: default='plan.json'.

[s81_expression_freeze.py](s81_expression_freeze.py)

The program freezes the validation-selected whole-expression interface and submit confirmation.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'expression_freeze.json').write_text(json.dumps(freeze, indent=2) + '\n')
(HERE / 'expression_submission.json').write_text(json.dumps(dict(array_job=job, audit_job=audit, expected_trials=360), indent=2) + '\n')
p.read_text()
p.read_bytes()

```

[s82_expression_test_array.sh](s82_expression_test_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprTest
#$ -l h_rt=00:50:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
index=$((SGE_TASK_ID-1))
case=$((index/2))
if (( index % 2 == 0 )); then size=1; else size=16; fi
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s79_expression_test_run.py --partition test --case "$case" --sizes "$size" --repetitions 5 --policies expression_frozen --stage expression_test

```

[s83_expression_test_summary.py](s83_expression_test_summary.py)

The program summarizes frozen supplied-expression confirmation without discarding failures.

The module defines these callable interfaces:

```python

def read(p)
def good(r)
def compare(numerator, denominator, size=None)

```

The imported project modules are `s39_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'expression_test_summary.json').write_text(json.dumps(out, indent=2) + '\n')
p.read_text()
(HERE / 'expression_test_validation.json').read_bytes()

```

[s84_expression_finalize.sh](s84_expression_finalize.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprFinal
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/expression_test_finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s80_expression_test_audit.py --stage expression_test
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s83_expression_test_summary.py

```

[s85_expression_report.py](s85_expression_report.py)

The program describes measured whole-expression reductions in the report.

The module defines these callable interfaces:

```python

def read(n)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_expression_results.tex').write_text('\n\n'.join(out) + '\n')
p.read_text()
p.write_text(text)
(HERE / n).read_text()

```

[s86_finish_documentation.py](s86_finish_documentation.py)

The program finishes release documentation after every declared comparison has been audited.

The module defines these callable interfaces:

```python

def read(n)
def value(c)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

p.write_text(text + '\n\n' + marker + '\n' + extra + '\n')
p.write_text(text + '\n\n' + marker + '\n' + brief + '\n\n' + transfer + '\n\n' + 'Code, raw measurements and checks: [' + link + '](' + link + ').\n')
p.write_text(text)
p.write_text(text + '\n\n' + marker3 + '\n' + finding + '\n')
(HERE / n).read_text()
p.read_text()

```

[s87_expression_plot.py](s87_expression_plot.py)

The program plots complete-cost ratios for the frozen whole-expression confirmation.

The imported external packages are `matplotlib`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--matched'`: action='store_true'.

These calls show the stored input and output interface:

```python

(HERE / ('expression_matched_summary.json' if args.matched else 'expression_test_summary.json')).read_text()

```

[s88_matched_expression_worker.py](s88_matched_expression_worker.py)

The program uses the same early master admission for learned and distance-selected seeds.

The imported project modules are `s69_expression_preflight`, `s78_expression_controls_worker`.

This entry point uses the paths and options set in its source.

[s89_matched_expression_run.py](s89_matched_expression_run.py)

The file provides counterbalanced complete trials, with bounded time, memory and scratch.

The module defines these callable interfaces:

```python

def write(p, x)
def limits()
def main()

```

The imported project modules are `s03_run`, `s36_evidence`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--partition'`: default='train'.
- `'--case'`: type=int; required=True.
- `'--sizes'`: default='16'.
- `'--repetitions'`: type=int; default=1.
- `'--policies'`: default='trim,tight,gate_disabled,pool_filter,ml_filter,ml_envelope'.
- `'--stage'`: default='expression_pilot'.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
(HERE / 'expression_matched_freeze.json').read_text()
(HERE / 'frozen_policy.json').read_text()
path.read_text(errors='replace')
(HERE / name).read_bytes()
(HERE / 'plan.json').read_bytes()
(HERE / 's88_matched_expression_worker.py').read_bytes()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s90_matched_expression_array.sh](s90_matched_expression_array.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprMatch
#$ -l h_rt=00:50:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
index=$((SGE_TASK_ID-1))
case=$((index/2))
if (( index % 2 == 0 )); then size=1; else size=16; fi
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s89_matched_expression_run.py --partition test --case "$case" --sizes "$size" --repetitions 5 --policies expression_frozen --stage expression_matched

```

[s91_matched_expression_audit.py](s91_matched_expression_audit.py)

The program validates supplied-expression seed choices and raw Kira exports.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`, `s08_verify`, `s39_records`, `s61_evidence_archive`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--stage'`: required=True.
- `'--plan'`: default='plan.json'.

[s92_matched_expression_summary.py](s92_matched_expression_summary.py)

The program summarizes frozen supplied-expression confirmation without discarding failures.

The module defines these callable interfaces:

```python

def read(p)
def good(r)
def compare(numerator, denominator, size=None)

```

The imported project modules are `s39_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'expression_matched_summary.json').write_text(json.dumps(out, indent=2) + '\n')
p.read_text()
(HERE / 'expression_matched_validation.json').read_bytes()

```

[s93_matched_expression_finalize.sh](s93_matched_expression_finalize.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraMatchFinal
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/expression_matched_finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s91_matched_expression_audit.py --stage expression_matched
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s92_matched_expression_summary.py

```

[s94_matched_expression_report.py](s94_matched_expression_report.py)

The program reports the confirmation with identical admission checks for both selectors.

The module defines these callable interfaces:

```python

def read(n)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(ROOT / 'report/kira_expression_matched.tex').write_text('\n\n'.join(parts) + '\n')
p.read_text()
p.write_text(text)
(HERE / 'matched_report_values.json').write_text(json.dumps(dict(interpretation=interpretation, full_pool=c, distance=dc, single_target=single, single_distance=single_distance, single_target_statement=single_statement), indent=2) + '\n')
(HERE / n).read_text()

```

[s95_release_checks.py](s95_release_checks.py)

The program checks all declared comparison outputs before publishing the release.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(ROOT / 'report/report.tex').read_text()
(HERE / 'release_validation.json').write_text(json.dumps(out, indent=2) + '\n')
p.read_text()
p.read_bytes()

```

[s96_prepare_release.sh](s96_prepare_release.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReleaseDocs
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/release_documents.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export LC_ALL=C LANG=C PYTHONIOENCODING=utf-8
ulimit -v 2097152
ulimit -f 131072
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s85_expression_report.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s94_matched_expression_report.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s35_document.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s86_finish_documentation.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s31_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py --matched
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s95_release_checks.py

```

## Data and supporting files

This folder contains 193 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.csv`: 1 entries.

- `.json`: 60 entries.

- `.lock`: 2 entries.

- `.log`: 17 entries.

- `.npz`: 2 entries.

- `.o15109644`: 1 entries.

- `.o15109645`: 1 entries.

- `.o15109663`: 1 entries.

- `.o15109664`: 1 entries.

- `.o15109667`: 1 entries.

- `.o15109668`: 1 entries.

- `.o15109674`: 1 entries.

- `.o15109695`: 1 entries.

- `.o15109697`: 1 entries.

- `.o15109702.1`: 1 entries.

- `.o15109702.2`: 1 entries.

- `.o15109702.3`: 1 entries.

- `.o15109702.4`: 1 entries.

- `.o15109702.5`: 1 entries.

- `.o15109702.6`: 1 entries.

- `.o15109980.1`: 1 entries.

- `.o15109980.10`: 1 entries.

- `.o15109980.11`: 1 entries.

- `.o15109980.12`: 1 entries.

- `.o15109980.13`: 1 entries.

- `.o15109980.14`: 1 entries.

- `.o15109980.15`: 1 entries.

- `.o15109980.16`: 1 entries.

- `.o15109980.17`: 1 entries.

- `.o15109980.18`: 1 entries.

- `.o15109980.19`: 1 entries.

- `.o15109980.2`: 1 entries.

- `.o15109980.20`: 1 entries.

- `.o15109980.21`: 1 entries.

- `.o15109980.22`: 1 entries.

- `.o15109980.23`: 1 entries.

- `.o15109980.24`: 1 entries.

- `.o15109980.3`: 1 entries.

- `.o15109980.4`: 1 entries.

- `.o15109980.5`: 1 entries.

- `.o15109980.6`: 1 entries.

- `.o15109980.7`: 1 entries.

- `.o15109980.8`: 1 entries.

- `.o15109980.9`: 1 entries.

- `.o15110075`: 1 entries.

- `.o15110079`: 1 entries.

- `.o15110100`: 1 entries.

- `.o15110144`: 1 entries.

- `.o15110161`: 1 entries.

- `.o15110183`: 1 entries.

- `.o15110184`: 1 entries.

- `.o15110185`: 1 entries.

- `.o15110186`: 1 entries.

- `.o15110187`: 1 entries.

- `.o15110188`: 1 entries.

- `.o15110189`: 1 entries.

- `.o15110221`: 1 entries.

- `.o15110236`: 1 entries.

- `.o15110286`: 1 entries.

- `.o15110287`: 1 entries.

- `.o15110329`: 1 entries.

- `.o15110345.1`: 1 entries.

- `.o15110345.2`: 1 entries.

- `.o15110345.3`: 1 entries.

- `.o15110345.4`: 1 entries.

- `.o15110345.5`: 1 entries.

- `.o15110345.6`: 1 entries.

- `.o15110549.1`: 1 entries.

- `.o15110549.10`: 1 entries.

- `.o15110549.11`: 1 entries.

- `.o15110549.12`: 1 entries.

- `.o15110549.13`: 1 entries.

- `.o15110549.14`: 1 entries.

- `.o15110549.15`: 1 entries.

- `.o15110549.16`: 1 entries.

- `.o15110549.17`: 1 entries.

- `.o15110549.18`: 1 entries.

- `.o15110549.19`: 1 entries.

- `.o15110549.2`: 1 entries.

- `.o15110549.20`: 1 entries.

- `.o15110549.21`: 1 entries.

- `.o15110549.22`: 1 entries.

- `.o15110549.23`: 1 entries.

- `.o15110549.24`: 1 entries.

- `.o15110549.3`: 1 entries.

- `.o15110549.4`: 1 entries.

- `.o15110549.5`: 1 entries.

- `.o15110549.6`: 1 entries.

- `.o15110549.7`: 1 entries.

- `.o15110549.8`: 1 entries.

- `.o15110549.9`: 1 entries.

- `.o15110588.1`: 1 entries.

- `.o15110588.10`: 1 entries.

- `.o15110588.11`: 1 entries.

- `.o15110588.12`: 1 entries.

- `.o15110588.13`: 1 entries.

- `.o15110588.14`: 1 entries.

- `.o15110588.15`: 1 entries.

- `.o15110588.16`: 1 entries.

- `.o15110588.17`: 1 entries.

- `.o15110588.18`: 1 entries.

- `.o15110588.19`: 1 entries.

- `.o15110588.2`: 1 entries.

- `.o15110588.20`: 1 entries.

- `.o15110588.21`: 1 entries.

- `.o15110588.22`: 1 entries.

- `.o15110588.23`: 1 entries.

- `.o15110588.24`: 1 entries.

- `.o15110588.3`: 1 entries.

- `.o15110588.4`: 1 entries.

- `.o15110588.5`: 1 entries.

- `.o15110588.6`: 1 entries.

- `.o15110588.7`: 1 entries.

- `.o15110588.8`: 1 entries.

- `.o15110588.9`: 1 entries.

- `no suffix`: 1 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.

## Child folders

- [adaptive_pilot](adaptive_pilot/README.md).

- [adaptive_validation](adaptive_validation/README.md).

- [combined_pilot](combined_pilot/README.md).

- [component_pilot](component_pilot/README.md).

- [cpp_initial](cpp_initial/README.md).

- [cpp_pilot](cpp_pilot/README.md).

- [cpp_pilot_v2](cpp_pilot_v2/README.md).

- [cpp_pilot_v3](cpp_pilot_v3/README.md).

- [cpp_v2](cpp_v2/README.md).

- [development_extra](development_extra/README.md).

- [evidence](evidence/README.md).

- [expression_matched](expression_matched/README.md).

- [expression_pilot](expression_pilot/README.md).

- [expression_preflight](expression_preflight/README.md).

- [expression_small](expression_small/README.md).

- [expression_test](expression_test/README.md).

- [expression_thresholds](expression_thresholds/README.md).

- [expression_v1](expression_v1/README.md).

- [expression_validation](expression_validation/README.md).

- [pilot](pilot/README.md).

- [preflight_pilot](preflight_pilot/README.md).

- [residual_pilot](residual_pilot/README.md).

- [results](results/README.md).

- [row_source_pilot](row_source_pilot/README.md).

- [structured_evidence](structured_evidence/README.md).

- [transfer_test](transfer_test/README.md).

- [validation](validation/README.md).
