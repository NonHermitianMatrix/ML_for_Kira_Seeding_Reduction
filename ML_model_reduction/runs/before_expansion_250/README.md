# before expansion 250

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

[s00_common.py](s00_common.py)

The file provides paths, bounded storage and reproducible file operations.

The module defines these callable interfaces:

```python

def read(p)
def config()
def rows(p)
def sha(p)
def write_json(p, value)
def atomic_torch(p, value)
def folder_size(path)
def storage_guard(full=False)
def status(stage, **kwargs)

```

The imported external packages are `torch`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
INTEGRALS = ROOT / 'integrals'
SPLIT = ROOT / 'ML_model_seed_selection/split_manifest.json'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

tmp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
torch.save(value, tmp)
pathlib.Path(p).read_text(encoding='utf-8')

```

[s01_state.py](s01_state.py)

The program encodes current matrix/actions and apply exact finite-field elementary row operations.

The module defines these callable interfaces:

```python

def indices(key)
def column(a)
def is_prime(p)
def clean_row(row, p, n)
def order_key(key)
def eliminate(destination, source, pivot, p)
def normalize_state(state, cfg=None)
def public_family(definition)
def family_features(text, bins)
def complexity(key)
def index_features(key, cfg)
def row_features(row, masters)
def feature_names(cfg=None)
def encode_state(state, cfg=None)
def state_from_step(step, identities, family, masters, prime)

```

The imported external packages are `numpy`.

The imported project modules are `s00_common`.

Import this helper module from the stage that uses it.

[s02_prepare_data.py](s02_prepare_data.py)

The program prepares only the existing training-family reduction states; replay every label.

The module defines these callable interfaces:

```python

def prepare_family(meta, cfg, signature)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s00_common`, `s01_state`.

The command accepts these parser options:

- `'--limit'`: type=int.

[s03_model.py](s03_model.py)

The file provides shared 32-component candidate encoder with pooled candidate context.

The module defines these callable interfaces:

```python

class ReductionSelector

```

The imported external packages are `torch`.

Import this helper module from the stage that uses it.

[s04_train.py](s04_train.py)

The program trains all prepared choice states, with deterministic group-boundary resume.

The module defines these callable interfaces:

```python

def batches(shards, indices, cfg)
def collate(shards, items, maximum)
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_common`, `s03_model`.

The command accepts these parser options:

- `'--resume'`: action='store_true'.

These calls show the stored input and output interface:

```python

torch.load(latest, map_location='cpu', weights_only=False)

```

[s05_predict.py](s05_predict.py)

The program returns all next-step probabilities; optionally apply the selected exact row operation.

The module defines these callable interfaces:

```python

class Predictor
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_common`, `s01_state`, `s03_model`.

The command accepts these parser options:

- `'state'`: type=pathlib.Path.
- `'--checkpoint'`: type=pathlib.Path.
- `'--apply'`: action='store_true'.
- `'--output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

torch.load(checkpoint or HERE / 'trained_model.pt', map_location='cpu', weights_only=False)
args.output.write_text(text, encoding='utf-8')

```

[s06_check.py](s06_check.py)

The file provides analytical and training-only checks; no held-out dataset is opened.

The module defines these callable interfaces:

```python

def toy()
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_common`, `s01_state`, `s03_model`.

This entry point uses the paths and options set in its source.

[s07_run_training.sh](s07_run_training.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTrain
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/runs/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
REDUCTION_PYTHON=.tools/seed-model/venv/bin/python
"$REDUCTION_PYTHON" ML_model_reduction/s06_check.py
"$REDUCTION_PYTHON" ML_model_reduction/s02_prepare_data.py
"$REDUCTION_PYTHON" ML_model_reduction/s04_train.py --resume

```

[s08_finalize.py](s08_finalize.py)

The program verifies trained artifacts and write completed-training report text; no held-out evaluation.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_common`, `s01_state`, `s05_predict`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(HERE / 'trained_model.pt', map_location='cpu', weights_only=False)
torch.load(HERE / 'runs/latest.pt', map_location='cpu', weights_only=False)
(ROOT / 'report/reduction_training.tex').write_text(text, encoding='utf-8')

```

[s09_finalize_report.sh](s09_finalize_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionReport
#$ -l h_rt=00:30:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/runs/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/s06_check.py
.tools/seed-model/venv/bin/python ML_model_reduction/s08_finalize.py
make -C report

```

[s10_train_all_loops.py](s10_train_all_loops.py)

The file provides warm-start the saved reduction model and optimizer for twenty expanded-data passes.

The module defines these callable interfaces:

```python

def batches(shards, indices, cfg)
def collate(shards, items, maximum)
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_common`, `s03_model`.

The command accepts these parser options:

- `'--resume'`: action='store_true'.

These calls show the stored input and output interface:

```python

torch.load(warm, map_location='cpu', weights_only=False)
torch.load(latest, map_location='cpu', weights_only=False)

```

[s11_run_all_loops.sh](s11_run_all_loops.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionAllLoops
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/runs/all_loops_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
python3 - <<'PY'
import json
from pathlib import Path
summary=json.loads(Path("integrals/higher_loops/integration_summary.json").read_text())
validation=json.loads(Path("integrals/higher_loops/validation.json").read_text())
assert summary["families"]==2100 and summary["targets"]==381272
assert validation["status"]=="passed" and len(validation["families"])==1100
PY
REDUCTION_PYTHON=.tools/seed-model/venv/bin/python
"$REDUCTION_PYTHON" ML_model_reduction/s02_prepare_data.py
"$REDUCTION_PYTHON" ML_model_reduction/s10_train_all_loops.py --resume

```

## Data and supporting files

- [config.json](config.json): This file sets the model or calculation options.

- [release_manifest.json](release_manifest.json): This file identifies the saved release files.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [data](data/README.md).

- [runs](runs/README.md).
