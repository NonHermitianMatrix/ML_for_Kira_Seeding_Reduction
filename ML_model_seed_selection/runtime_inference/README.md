# runtime inference

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

[s00_vector_seed.py](s00_vector_seed.py)

The program constructs unchanged seed index features with bounded NumPy arrays.

The module defines these callable interfaces:

```python

def index_batch(indices, cfg)
class VectorSeed

```

The imported external packages are `numpy`.

The imported project modules are `s01_fast_seed`, `s21_seed_loader`.

These source constants locate inputs and outputs:

```python

ROOT = pathlib.Path(__file__).resolve().parents[2]

```

Import this helper module from the stage that uses it.

[s01_verify.py](s01_verify.py)

The program checks bitwise feature, embedding, probability and seed-decision parity.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s00_vector_seed`, `s01_fast_seed`, `s04_records`, `s07_seed`, `s21_seed_loader`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'parity.json').write_text(json.dumps(result, indent=2) + '\n')
(ROOT / 'Kira_comparison/multiloop_native/families.json').read_text()
(HERE / 's00_vector_seed.py').read_bytes()

```

[s02_seed_runtime.cpp](s02_seed_runtime.cpp)

The file provides bounded inference for the existing float32 seed network.

The required headers are `algorithm`, `cmath`, `cstdint`, `fstream`, `map`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

The public compiled interface is:

```cpp

extern "C" {

```

Use the parent stage guide for the build order and input records.

[s03_export_compiled.py](s03_export_compiled.py)

The program exports unchanged float32 weights into a bounded portable runtime archive.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'compiled_weights.bin').write_bytes(data)
(HERE / 'compiled_export.json').write_text(json.dumps(record, indent=2) + '\n')
(source / 'seed_export.json').read_text()
(source / 'seed_weights.npz').read_bytes()

```

[s04_compiled_seed.py](s04_compiled_seed.py)

The program applies the unchanged neural seed model without NumPy startup in production.

The module defines these callable interfaces:

```python

class CompiledSeed
def choose(definition, masters, targets, spec, closure=False, use_model=True, threshold=0.01)

```

The imported project modules are `s01_fast_seed`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'compiled_export.json').read_text()

```

[s05_verify_compiled.py](s05_verify_compiled.py)

The program compares compiled neural inference with the unchanged NumPy network.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s00_vector_seed`, `s03_records`, `s04_compiled_seed`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/integrated_runtime'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / ('compiled_threshold_parity.json' if '--expanded' in sys.argv else 'compiled_parity.json')).write_text(json.dumps(record, indent=2) + '\n')
(EXP / 'families.json').read_text()
(HERE / 'compiled_weights.bin').read_bytes()
(ROOT / '.tools/kira-seed-inference/libseed.so').read_bytes()
(HERE / 's02_seed_runtime.cpp').read_bytes()

```

[s06_build_compiled.sh](s06_build_compiled.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedCppBuild
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 1572864
ulimit -c 0
mkdir -p .tools/kira-seed-inference
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s03_export_compiled.py
g++ -std=c++17 -O3 -ffp-contract=off -fPIC -shared -static-libstdc++ -static-libgcc -Wl,--exclude-libs,ALL ML_model_seed_selection/runtime_inference/s02_seed_runtime.cpp -o .tools/kira-seed-inference/libseed.so
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s05_verify_compiled.py

```

[s07_cold_component.py](s07_cold_component.py)

The program measures a fresh-process seed decision, including imports and model loading.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_vector_seed`, `s03_records`, `s04_compiled_seed`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'backend'`: The parser accepts a value..
- `'case'`: The parser accepts a value..
- `'size'`: type=int.

These calls show the stored input and output interface:

```python

(exp / 'families.json').read_text()

```

[s08_cold_benchmark.py](s08_cold_benchmark.py)

The program compares cold seed backends with identical candidates and decisions.

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

(HERE / 'cold_benchmark.json').write_text(json.dumps(result, indent=2) + '\n')
(ROOT / 'Kira_comparison/integrated_runtime/families.json').read_text()
(HERE / 'compiled_parity.json').read_bytes()

```

[s09_cold_benchmark.sh](s09_cold_benchmark.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedColdCheck
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s05_verify_compiled.py --expanded
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s08_cold_benchmark.py

```

[s10_fit_thresholds.py](s10_fit_thresholds.py)

The program fits execution thresholds from complete native training-workflow cost.

The module defines these callable interfaces:

```python

def key(case, size=32)
def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/integrated_runtime'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'threshold_policy.json').write_text(json.dumps(result, indent=2) + '\n')
(EXP / 'families.json').read_text()
base_path.read_bytes()
p.read_bytes()

```

[s11_shared_runtime.cpp](s11_shared_runtime.cpp)

The file provides bounded inference for the existing float32 seed network.

The required headers are `algorithm`, `cmath`, `cstdint`, `fstream`, `map`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

The public compiled interface is:

```cpp

extern "C" {

```

Use the parent stage guide for the build order and input records.

[s12_shared_seed.py](s12_shared_seed.py)

The program applies the unchanged neural seed model without NumPy startup in production.

The module defines these callable interfaces:

```python

class CompiledSeed
def choose(definition, masters, targets, spec, closure=False, use_model=True, threshold=0.01)

```

The imported project modules are `s01_fast_seed`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'compiled_export.json').read_text()

```

[s13_lane_runtime.cpp](s13_lane_runtime.cpp)

The file provides bounded inference for the existing float32 seed network.

The required headers are `algorithm`, `cmath`, `cstdint`, `fstream`, `map`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

The public compiled interface is:

```cpp

extern "C" {

```

Use the parent stage guide for the build order and input records.

[s14_lane_seed.py](s14_lane_seed.py)

The program applies the unchanged neural seed model without NumPy startup in production.

The module defines these callable interfaces:

```python

class CompiledSeed
def choose(definition, masters, targets, spec, closure=False, use_model=True, threshold=0.01)

```

The imported project modules are `s01_fast_seed`, `s07_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(HERE / 'compiled_export.json').read_text()

```

## Data and supporting files

- [cold_benchmark.json](cold_benchmark.json): This file contains structured records from the parent calculation.

- [compiled_export.json](compiled_export.json): This file contains structured records from the parent calculation.

- [compiled_parity.json](compiled_parity.json): This file contains structured records from the parent calculation.

- [compiled_threshold_parity.json](compiled_threshold_parity.json): This file contains structured records from the parent calculation.

- [compiled_weights.bin](compiled_weights.bin): This file contains a saved model or its description.

- [parity.json](parity.json): This file contains structured records from the parent calculation.

- [threshold_policy.json](threshold_policy.json): This file contains structured records from the parent calculation.
