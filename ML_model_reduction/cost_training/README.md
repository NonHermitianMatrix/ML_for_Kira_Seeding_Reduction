# cost training

This folder contains training inputs or saved training results.
Keep the stored family division unchanged.

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

[reduction_cost.patch](reduction_cost.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[reduction_tree.patch](reduction_tree.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_cost_policy.h](s00_cost_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s01_build.py](s01_build.py)

The program patches source selection inside native Kira and reuse the responsive shutdown.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / os.getenv('KIRA_COST_BUILD_DIR', '.tools/kira-cost-training')
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

[s02_build.sh](s02_build.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s01_build.py

```

[s03_train.py](s03_train.py)

The program fits a small cost ranker to exact counterfactual Kira updates.

The module defines these callable interfaces:

```python

def load(paths)
def metrics(groups, mean, scale, w, gain)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--data'`: type=pathlib.Path; required=True.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model.json').write_text(json.dumps(model, indent=2) + '\n')
(HERE / 'trained_weights.txt').write_text('\n'.join(lines) + '\n')
(HERE / 'training_results.json').write_text(json.dumps(evaluation, indent=2) + '\n')
p.read_bytes()

```

[s04_predict.py](s04_predict.py)

The program returns probabilities and the chosen native source-row candidate.

The module defines these callable interfaces:

```python

def predict(features, model=None)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s08_train_tree`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'input'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model.json').read_text()
a.input.read_text()

```

[s05_fit.sh](s05_fit.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostFit
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s03_train.py --data Kira_comparison/multiloop_native/training

```

[s06_train_continuation.py](s06_train_continuation.py)

The program trains on measured remaining forward-elimination operations in exact Kira continuations.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`.

The imported project modules are `s03_train`, `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trained_model.json').write_text(json.dumps(model, indent=2) + '\n')
(HERE / 'trained_weights.txt').write_text('\n'.join([f'18 0 {gain:.17g}'] + [' '.join((format(v, '.17g') for v in a)) for a in [mean, scale, w]]) + '\n')
(HERE / 'training_results.json').write_text(json.dumps(result, indent=2) + '\n')
p.read_bytes()

```

[s07_fit_continuation.sh](s07_fit_continuation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostFit2
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s06_train_continuation.py

```

[s08_train_tree.py](s08_train_tree.py)

The program fits a small nonlinear cost model from the same exact continuations.

The module defines these callable interfaces:

```python

def data()
def fit(x, y, wt, depth, minleaf)
def predict(nodes, x)
def evaluate(groups, nodes, gain)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s04_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'tree_candidate_model.json').write_text(json.dumps(model, indent=2) + '\n')
(HERE / 'tree_candidate_weights.txt').write_text('\n'.join(lines) + '\n')
(HERE / 'tree_candidate_results.json').write_text(json.dumps(result, indent=2) + '\n')
p.read_bytes()

```

[s09_fit_tree.sh](s09_fit_tree.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostTree
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s08_train_tree.py

```

[s10_tree_policy.h](s10_tree_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s11_build_tree.sh](s11_build_tree.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostTreeB
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COST_BUILD_DIR=.tools/kira-cost-tree KIRA_COST_HEADER=s10_tree_policy.h
export KIRA_COST_BUILD_RECORD=tree_build.json KIRA_COST_PATCH=reduction_tree.patch
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s01_build.py

```

[s12_promote_tree.py](s12_promote_tree.py)

The program preserves the linear continuation model and install the validated tree candidate.

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

(HERE / 'trained_model.json').write_text(json.dumps(model, indent=2) + '\n')
(HERE / 'tree_promotion.json').write_text(json.dumps(record, indent=2) + '\n')
(HERE / 'tree_candidate_results.json').read_text()
(HERE / 'trained_model.json').read_text()
(old / 'trained_weights.txt').read_bytes()
(HERE / 'trained_weights.txt').read_bytes()
(ROOT / '.tools/kira-cost-tree/kira').read_bytes()

```

## Data and supporting files

- [COPYING](COPYING): This file supports the calculation described in the parent guide.

- [build.json](build.json): This file contains structured records from the parent calculation.

- [feature_schema.json](feature_schema.json): This file contains structured records from the parent calculation.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_weights.txt](trained_weights.txt): This file contains a saved model or its description.

- [training_results.json](training_results.json): This file records training progress or training inputs.

- [tree_build.json](tree_build.json): This file contains structured records from the parent calculation.

- [tree_candidate_model.json](tree_candidate_model.json): This file contains a saved model or its description.

- [tree_candidate_results.json](tree_candidate_results.json): This file contains structured records from the parent calculation.

- [tree_candidate_weights.txt](tree_candidate_weights.txt): This file contains a saved model or its description.

- [tree_promotion.json](tree_promotion.json): This file contains structured records from the parent calculation.

## Child folders

- [immediate_cost_v1](immediate_cost_v1/README.md).

- [linear_continuation_v2](linear_continuation_v2/README.md).

- [model_test](model_test/README.md).
