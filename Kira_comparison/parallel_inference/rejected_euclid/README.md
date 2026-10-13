# rejected euclid

This folder retains an earlier stage, development check or saved comparison.
Use its records to interpret that stage.
Use the current parent application for a new calculation.

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

[reduction_parallel.patch](reduction_parallel.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_check_arithmetic.cpp](s00_check_arithmetic.cpp)

The file provides exact checks for field inversion and all source-row features.

The required headers are `string`, `vector`, `algorithm`, `iostream`, `random`, `stdexcept`, `chrono`, `iomanip`, `s15_shared_modular.h`, `s17_euclid_modular.h`.

The matching build script compiles this file into an executable.

Use the parent stage guide for the build order and input records.

[s01_check_seed.py](s01_check_seed.py)

The program checks bitwise probabilities and masks against the preceding compiled network.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s07_seed`, `s12_shared_seed`, `s14_lane_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent / 'integrated_runtime'
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'seed_parity.json').write_text(json.dumps(data, indent=2) + '\n')
(EXP / 'families.json').read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/compiled_weights.bin').read_bytes()
(ROOT / '.tools/kira-parallel-inference/libseed.so').read_bytes()

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
KIRA_RUNTIME_BUILD_DIR=.tools/kira-parallel-inference KIRA_RUNTIME_HEADER=s18_euclid_policy.h KIRA_COST_BUILD_RECORD=../parallel_inference/build.json KIRA_COST_PATCH=../parallel_inference/reduction_parallel.patch python3 Kira_comparison/integrated_runtime/s00_build.py

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

## Data and supporting files

- [adoption.json](adoption.json): This file contains structured records from the parent calculation.

- [arithmetic_check.json](arithmetic_check.json): This file records checks of the corresponding calculation.

- [build.json](build.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [seed_parity.json](seed_parity.json): This file records seed information or seed checks.

- [validation_summary.json](validation_summary.json): This file contains structured records from the parent calculation.

## Child folders

- [validation](validation/README.md).
