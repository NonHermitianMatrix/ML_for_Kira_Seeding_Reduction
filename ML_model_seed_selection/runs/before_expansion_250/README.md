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

[s00_prepare_data.py](s00_prepare_data.py)

The program audits seed supervision and prepare a reproducible grouped 70:30 split; it does not fit a model.

The module defines these callable interfaces:

```python

def read(path)
def rows(path)
def sha(path)
def group_for(d)
def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / 'integrals'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

path.read_text(encoding='utf-8')
(HERE / name).write_text(json.dumps(content, indent=2, sort_keys=True) + '\n', encoding='utf-8')

```

[s01_data.py](s01_data.py)

The file provides streaming inputs with a strict boundary between problem features and reference labels.

The module defines these callable interfaces:

```python

def read(path)
def config()
def rows(path)
def text_features(text, bins)
def index_features(indices, cfg)
def public_family(definition, master_basis)
def encode_shared(family, seeds, cfg)
def encode(target, family, seeds, cfg, shared=None)
def labels(reference, seeds)
def family_records(meta, cfg, shuffle_seed=None)
def examples(split, cfg, epoch=None, start=0)
def find_input(identifier)
def verify_sources(split=None)
def storage_guard()

```

The imported external packages are `torch`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / 'integrals'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

path.read_text(encoding='utf-8')
(HERE / 'split_manifest.json').read_bytes()

```

[s02_model.py](s02_model.py)

The file provides small shared neural scorer; every output is a reference-set membership probability.

The module defines these callable interfaces:

```python

class SeedSelector
def reference_loss(logits, y)
def binary_decisions(probabilities)

```

The imported external packages are `torch`.

Import this helper module from the stage that uses it.

[s03_train.py](s03_train.py)

The program trains the seed model on the training split only; save resumable and final weights here.

The module defines these callable interfaces:

```python

def atomic_json(path, value)
def train(epochs=None, resume=False)

```

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`.

The command accepts these parser options:

- `'--epochs'`: type=int.
- `'--resume'`: action='store_true'.

These calls show the stored input and output interface:

```python

temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
torch.load(str(checkpoint), map_location='cpu')
torch.save(payload, str(temp))
tmp.write_text(''.join((json.dumps(r) + '\n' for r in history)), encoding='utf-8')
torch.save(final, str(temp))
p.read_bytes()

```

[s04_predict.py](s04_predict.py)

The program ranks an input target's bounded candidate pool using an explicitly supplied trained checkpoint.

The module defines these callable interfaces:

```python

def load_model(path)
def main()

```

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`.

The command accepts these parser options:

- `'--checkpoint'`: type=pathlib.Path; required=True.
- `'--target'`: required=True.
- `'--seeds'`: type=pathlib.Path; help="Optional public candidate list in {'indices': [...]} form".

These calls show the stored input and output interface:

```python

torch.load(str(path), map_location='cpu')
(HERE / 'split_manifest.json').read_bytes()

```

[s05_evaluate.py](s05_evaluate.py)

The file provides future held-out comparison with recorded sufficient sets; no exact-reduction claim.

The module defines these callable interfaces:

```python

def confidence_bins(probabilities, labels)
def seed_metrics(probabilities, labels)
def main()

```

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`, `s04_predict`.

The command accepts these parser options:

- `'--checkpoint'`: type=pathlib.Path; required=True.
- `'--output'`: type=pathlib.Path; default=HERE / 'runs' / 'test_metrics.json'.

These calls show the stored input and output interface:

```python

args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')

```

[s06_check.py](s06_check.py)

The file provides implementation checks only: no optimizer, learned checkpoint or performance estimate.

The module defines these callable interfaces:

```python

class ModelChecks
def main()

```

The imported external packages are `torch`.

The imported project modules are `s00_prepare_data`, `s01_data`, `s02_model`, `s05_evaluate`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'implementation_checks.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')

```

[s07_run.sh](s07_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedModel
#$ -l h_rt=24:00:00,h_data=4G
#$ -j y
#$ -o .tools/seed-model/logs
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
SEED_PYTHON=.tools/seed-model/venv/bin/python
MODE=check
if (( $# )); then MODE="$1"; fi
case "$MODE" in
  prepare) timeout 1100s "$SEED_PYTHON" ML_model_seed_selection/s00_prepare_data.py ;;
  check) timeout 600s "$SEED_PYTHON" ML_model_seed_selection/s06_check.py ;;
  train) shift; timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s03_train.py "$@" ;;
  evaluate) shift; timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s05_evaluate.py "$@" ;;
  *) echo "Use prepare, check, train or evaluate." >&2; exit 2 ;;
esac

```

[s08_setup_environment.sh](s08_setup_environment.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedEnv
#$ -l h_rt=00:20:00,h_data=3G
#$ -j y
#$ -o .tools/seed-model/logs
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2621440
ulimit -f 786432
ulimit -c 0
mkdir -p .tools/seed-model/tmp
export TMPDIR="$PWD/.tools/seed-model/tmp"
python3 -m venv --system-site-packages .tools/seed-model/venv
.tools/seed-model/venv/bin/python -m pip install --no-cache-dir --ignore-installed --no-deps --index-url https://download.pytorch.org/whl/cpu 'torch==2.2.2+cpu'
.tools/seed-model/venv/bin/python -c 'import torch,numpy;print("torch",torch.__version__,"numpy",numpy.__version__)'

```

[s09_check_training_inputs.py](s09_check_training_inputs.py)

The program checks training input reuse and resume ordering without evaluating the test split.

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(out / 'input_checks.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')

```

[s10_finalize_training.py](s10_finalize_training.py)

The program verifies the saved training artifact and update status documentation; never run testing.

The imported external packages are `torch`.

The imported project modules are `s01_data`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

torch.load(str(model_path), map_location='cpu')
(HERE / 'trained_model.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')
p.write_text(text[:start] + paragraph + text[end:], encoding='utf-8')
p.write_text(text[:start] + para + text[end:], encoding='utf-8')
model_path.read_bytes()

```

[s11_run_training.sh](s11_run_training.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedTrain
#$ -l h_rt=24:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
SEED_PYTHON=.tools/seed-model/venv/bin/python
"$SEED_PYTHON" ML_model_seed_selection/s09_check_training_inputs.py
if [[ -f ML_model_seed_selection/runs/latest.pt ]]; then
  timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s03_train.py --resume
else
  timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s03_train.py
fi
"$SEED_PYTHON" ML_model_seed_selection/s10_finalize_training.py
{
git -c gc.auto=0 add -- ML_model_seed_selection/trained_model.pt ML_model_seed_selection/trained_model.json ML_model_seed_selection/runs README.md ML_model_seed_selection/README.md
git -c gc.auto=0 commit -q -m 'Save seed-selection model after ten training epochs'
git -c pack.threads=1 -c pack.windowMemory=64m -c pack.deltaCacheSize=16m -c gc.auto=0 push origin main
} > .tools/seed-training/publish.log 2>&1

```

[s12_prepare_features.py](s12_prepare_features.py)

The program prepares bounded immutable features using training families only.

The module defines these callable interfaces:

```python

def sha(p)
def write(p, obj)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s01_data`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

t.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')
np.savez_compressed(f, **arrays)
p.read_bytes()

```

[s13_batch.py](s13_batch.py)

The file provides masked batch execution of the existing seed scorer, with identical features and weights.

The module defines these callable interfaces:

```python

def collate(z, items)
def forward(model, x, mask, shared)
def verify(model, z)

```

The imported external packages are `numpy`, `torch`.

Import this helper module from the stage that uses it.

[s14_train_all_loops.py](s14_train_all_loops.py)

The program continues saved weights and optimizer for twenty complete passes over expanded training data.

The module defines these callable interfaces:

```python

def savept(path, obj)
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s01_data`, `s02_model`, `s12_prepare_features`, `s13_batch`.

The command accepts these parser options:

- `'--pilot'`: action='store_true'.

These calls show the stored input and output interface:

```python

torch.save(obj, tmp)
torch.load(warm, map_location='cpu', weights_only=False)
torch.load(checkpoint, map_location='cpu', weights_only=False)

```

[s15_run_all_loops.sh](s15_run_all_loops.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedAllLoops
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/all_loops_scheduler.log
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
if [[ ! -f ML_model_seed_selection/runs/all_loops_latest.pt ]]; then
  .tools/seed-model/venv/bin/python ML_model_seed_selection/s12_prepare_features.py
fi
.tools/seed-model/venv/bin/python ML_model_seed_selection/s14_train_all_loops.py "$@"

```

[s16_validate_all_loops.py](s16_validate_all_loops.py)

The program validates the expanded-data checkpoint and preserve its training provenance.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`, `s12_prepare_features`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(HERE / 'trained_model.pt', map_location='cpu', weights_only=False)
torch.load(HERE / 'runs/all_loops_latest.pt', map_location='cpu', weights_only=False)

```

[s17_run_batch_pilot.sh](s17_run_batch_pilot.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraBatchPilot
#$ -l h_rt=00:05:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/batch_pilot_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_seed_selection/s14_train_all_loops.py --pilot

```

[s18_validate_mixed_batches.py](s18_validate_mixed_batches.py)

The program checks batched seed scores and derivatives on mixed-length training examples.

The module defines these callable interfaces:

```python

def sha(p)
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s01_data`, `s02_model`, `s13_batch`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'runs/all_loops_latest.pt').read_bytes()
torch.load(io.BytesIO(payload), map_location='cpu', weights_only=False)
(HERE / 'runs/mixed_batch_validation.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
p.read_bytes()

```

[s19_run_batch_validation.sh](s19_run_batch_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraMixedBatchCheck
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/mixed_batch_validation.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_seed_selection/s18_validate_mixed_batches.py

```

## Data and supporting files

- [config.json](config.json): This file sets the model or calculation options.

- [data_audit.json](data_audit.json): This file records checks of the corresponding calculation.

- [release_manifest.json](release_manifest.json): This file identifies the saved release files.

- [source_hashes.json](source_hashes.json): This file contains structured records from the parent calculation.

- [split_manifest.json](split_manifest.json): This file lists related records and their identifiers.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [data](data/README.md).

- [runs](runs/README.md).
