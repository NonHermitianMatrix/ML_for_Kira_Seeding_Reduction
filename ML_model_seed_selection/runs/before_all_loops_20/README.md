# before all loops 20

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

## Data and supporting files

- [config.json](config.json): This file sets the model or calculation options.

- [data_audit.json](data_audit.json): This file records checks of the corresponding calculation.

- [source_hashes.json](source_hashes.json): This file contains structured records from the parent calculation.

- [split_manifest.json](split_manifest.json): This file lists related records and their identifiers.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_model.pt](trained_model.pt): This file contains a saved model or its description.

## Child folders

- [runs](runs/README.md).
