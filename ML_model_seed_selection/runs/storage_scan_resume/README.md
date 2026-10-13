# storage scan resume

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

[s01_data_before.py](s01_data_before.py)

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

## Data and supporting files

- [checkpoint_before.pt](checkpoint_before.pt): This file contains a saved model or its description.

- [migration.json](migration.json): This file contains structured records from the parent calculation.

- [verification.json](verification.json): This file records the independent checks.
