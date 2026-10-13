# integrals

This folder contains the integral collection and its readers.
The collection has 17,100 family instances, 57,979 family-local master entries and 2,301,272 targets.
Training uses 1,610,890 targets from 11,963 families.
Testing uses 690,382 targets from 5,137 families.

`master_integrals/` contains family definitions and master bases.
`target_integrals/` contains the targets.
`master_to_target/` contains coefficients, identities, seeds and reduction steps.
The family and target identifiers connect these records.
`training/` and `testing/` contain links to the original data.
Keep each family in its assigned group.

The high-loop additions use restricted coupled vacuum integrals.
Their massive denominators share one momentum sum.
The collection does not cover every scattering topology.
A recorded construction gives a sufficient reduction path.
It does not prove a minimum number of operations.

Use `s01_read_data.py` to read the collection.
Use `s02_validate.py` to check the stored layout and links.
The numbered expansion folders contain the generation procedures.
Do not run an earlier expansion to replace the current collection.

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

[s00_reorganize.py](s00_reorganize.py)

The program reorganizes the existing checked collection without generating new integrals.

The module defines these callable interfaces:

```python

def read(path)
def encoded(value)
def sha(data)
def file_sha(path)
def put(path, data)
def write(path, value)
def zipped(path, data)
def archive(path, files)
def rows(data)
def guard()
def source_catalog(source)
def old_family(source, entry)
def locations(name)
def family_entry(old)
def prepare(source)
def convert(source, old)
def main()

```

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent

```

The command accepts these parser options:

- `'--source'`: type=Path; default=PROJECT.
- `'--prepare'`: action='store_true'.
- `'--family'`: action='append'.
- `'--batch-index'`: type=int; default=int(os.environ.get('SGE_TASK_ID', '1')) if os.environ.get('SGE_TASK_ID', '1').isdigit() else 1.
- `'--batch-size'`: type=int; default=50.

These calls show the stored input and output interface:

```python

tmp.write_bytes(data)
Path(path).read_text(encoding='utf-8')
(source / 'Expanded_Integrals/splits.json').read_bytes()
(source / 'Expanded_Integrals/split_overlap_witnesses.json').read_bytes()
p.read_bytes()

```

[s01_read_data.py](s01_read_data.py)

The program reads the unified integral collection on Hoffman.

The module defines these callable interfaces:

```python

def records(family, kind='inputs')
def linked_target(identifier)
def main()

```

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--family'`: The parser accepts a value..
- `'--kind'`: choices=list(FILES); default='inputs'.
- `'--target'`: help='Return one target with its master coefficients, seeds and elimination trace.'.
- `'--limit'`: type=int; default=1.

[s02_validate.py](s02_validate.py)

The program verifies the unified layout, all links and unchanged scientific records.

The module defines these callable interfaces:

```python

def lines(path)
def content(path)
def link(value)
def unchanged_fields(before, after, changed, added=())
def compare_original(entry, raw, supp, inputs, refs, traces)
def verify_family(entry, source=None, original=None)
def main()

```

The imported project modules are `s00_reorganize`, `s01_read_data`, `s10_validate_collection`.

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parent

```

The command accepts these parser options:

- `'--compare-source'`: type=Path.
- `'--family'`: action='append'.

These calls show the stored input and output interface:

```python

path.read_bytes()
(ROOT / 'master_integrals/families' / name / filename).read_bytes()

```

[s03_run_reorganization.sh](s03_run_reorganization.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N IntegralLayout
#$ -l h_rt=00:20:00,h_data=2G
#$ -j y
#$ -o .tools/integrals-layout/logs
set -euo pipefail
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
timeout 1100s python3 integrals/s00_reorganize.py "$@"

```

[s04_run_validation.sh](s04_run_validation.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N CheckIntegralLayout
#$ -l h_rt=00:25:00,h_data=2G
#$ -j y
#$ -o .tools/integrals-layout/logs
set -euo pipefail
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
timeout 1400s python3 integrals/s02_validate.py "$@"

```

[s05_prepare_model_splits.py](s05_prepare_model_splits.py)

The program creates non-overlapping train/test directory views without copying integral data.

The module defines these callable interfaces:

```python

def read(path)
def write(path, obj)
def original(path)
def main()

```

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parent
MODEL = ROOT.parent / 'ML_model_seed_selection'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')
path.read_text(encoding='utf-8')
(ROOT / name / 'README.md').write_text(text, encoding='utf-8')

```

## Data and supporting files

- [catalog.json](catalog.json): This file lists the integral collection.

- [families.json](families.json): This file defines the families in this collection.

- [model_split_summary.json](model_split_summary.json): This file gives the training and testing counts.

- [splits.json](splits.json): This file contains structured records from the parent calculation.

- [validation_summary.json](validation_summary.json): This file contains structured records from the parent calculation.

## Child folders

- [expansion_1000](expansion_1000/README.md).

- [expansion_250](expansion_250/README.md).

- [higher_loops](higher_loops/README.md).

- [master_integrals](master_integrals/README.md).

- [master_to_target](master_to_target/README.md).

- [target_integrals](target_integrals/README.md).

- [testing](testing/README.md).

- [training](training/README.md).
