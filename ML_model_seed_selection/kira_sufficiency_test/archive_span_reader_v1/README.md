# archive span reader v1

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

[s02_common.py](s02_common.py)

The file provides frozen inputs, bounded exact rational arithmetic, and seed-filtered systems.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def write(p, v)
def rows(p)
def family_file(fid, name)
def index_key(a)
def load_family(meta, prediction_entry, limit=None)
def literal(n)
def validate_expression(s)
def add(a, b, sign=1)
def mul(a, b)
def power(a, n)
def normalize(a, b)
def rational(s)
def exact_equal(left, right)
def exact_zero(s)
def clear_caches()
def selected_blocks(family)

```

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
DATA = ROOT / 'integrals'
WORK = ROOT / '.tools/kira-seed-sufficiency'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

tmp.write_text(json.dumps(v, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
Path(p).read_text(encoding='utf-8')

```

[s03_kira_adapter.py](s03_kira_adapter.py)

The program exports disjoint seed selections and read Kira's exact symbolic reductions.

The module defines these callable interfaces:

```python

def allocated(p)
def batches(blocks, limit=50000)
def export(family, blocks, w, quotient=True)
def run_once(w, timeout=600, scratch_limit=67108864)
def run_kira(w, timeout=600, scratch_limit=67108864)
def parse_output(path)
def assess(family, manifest, output, reference_by_id)
def assess_span(family, manifest, output, reference_by_id)

```

The imported project modules are `s02_common`, `s08_verify`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'targets').write_text(''.join(('%d\n' % i for i in targetmap)))
(w / 'masters').write_text(''.join(('%d\n' % i for i in basis)))
(w / 'jobs.yaml').write_text(JOBS)
(w / 'run.log').read_text(errors='replace')

```

[s06_evaluate.py](s06_evaluate.py)

The program freezes the solver protocol and evaluate disjoint held-out systems on Hoffman.

The module defines these callable interfaces:

```python

def protocol()
def output_allocated(folder)
def bounded_gzip(path, binary=False)
def save_gz(path, value)
def process(meta, prediction_entry, dest, scratch)
def worker(index)

```

The imported project modules are `s03_kira_adapter`, `s08_verify`.

The command accepts these parser options:

- `'--freeze'`: action='store_true'.
- `'--worker'`: type=int.

These calls show the stored input and output interface:

```python

Path('/proc/meminfo').read_text()

```

[s08_verify.py](s08_verify.py)

The file provides independent finite-field checks of the symbolic coefficients exported by Kira.

The module defines these callable interfaces:

```python

def evaluate(expression, variables, prime)
def check_records(records, references)
def nonzero_witness(expression, samples)
def reduced(row, basis)
def insert_row(row, basis)
def check_span_records(family, blocks, records, references)

```

The imported project modules are `s02_common`.

Import this helper module from the stage that uses it.

## Data and supporting files

- [protocol.json](protocol.json): This file contains structured records from the parent calculation.

- [retained_results.json](retained_results.json): This file contains structured records from the parent calculation.

- [worker_00.json](worker_00.json): This file contains structured records from the parent calculation.

- [worker_01.json](worker_01.json): This file contains structured records from the parent calculation.

- [worker_03.json](worker_03.json): This file contains structured records from the parent calculation.

- [worker_05.json](worker_05.json): This file contains structured records from the parent calculation.

- [worker_07.json](worker_07.json): This file contains structured records from the parent calculation.

- [worker_08.json](worker_08.json): This file contains structured records from the parent calculation.

- [worker_09.json](worker_09.json): This file contains structured records from the parent calculation.

- [worker_10.json](worker_10.json): This file contains structured records from the parent calculation.

- [worker_11.json](worker_11.json): This file contains structured records from the parent calculation.

- [worker_12.json](worker_12.json): This file contains structured records from the parent calculation.

- [worker_13.json](worker_13.json): This file contains structured records from the parent calculation.

- [worker_14.json](worker_14.json): This file contains structured records from the parent calculation.

- [worker_15.json](worker_15.json): This file contains structured records from the parent calculation.
