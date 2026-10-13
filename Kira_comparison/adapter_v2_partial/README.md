# adapter v2 partial

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

[s00_prepare.py](s00_prepare.py)

The program freezes outcome-independent held-out cases, models, and resource limits.

The module defines these callable interfaces:

```python

def sha(p)
def key(s)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'ML_model_seed_selection/split_manifest.json').read_text()
out.write_text(json.dumps(plan, indent=2) + '\n')
p.read_bytes()
out.read_text()

```

[s01_common.py](s01_common.py)

The file provides public inputs and exact coefficient arithmetic for paired Kira comparisons.

The module defines these callable interfaces:

```python

def read(p)
def write(p, v)
def sha(p)
def load_module(name, path)
def ranking(s)
def load_case(case, size)
def connected(eqs, targets, masters)
def rational_rows(terms)
def expression_terms(row)
def exact_check(rows, family)
def sample_point(definition)

```

The imported external packages are `sympy`.

The imported project modules are `s02_common`, `s03_kira_adapter`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / 'integrals'
SUFF = ROOT / 'ML_model_seed_selection/kira_sufficiency_test'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

t.write_text(json.dumps(v, indent=2, allow_nan=False) + '\n')
pathlib.Path(p).read_text()

```

[s02_worker.py](s02_worker.py)

The file provides one isolated symbolic reduction, with live inference and exact fallback.

The module defines these callable interfaces:

```python

def kira_run(w, plan)
def supplied(family, targets, selected, w, plan)
def seed_select(fam)
def reduce_targets(fam, learned=True)
def native(fam, trim, w, plan)
def main()

```

The imported external packages are `sympy`, `torch`.

The imported project modules are `s01_common`, `s01_state`, `s05_predict`, `s08_verify`.

The command accepts these parser options:

- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(w / 'run.log').read_text(errors='replace')
torch.load(ROOT / 'ML_model_seed_selection/trained_model.pt', map_location='cpu', weights_only=False)
(w / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(w / 'config/kinematics.yaml').write_text(json.dumps(kin))
(w / 'targets').write_text(''.join((label(a) + '\n' for a in component)))
(w / 'masters').write_text(''.join((label(a) + '\n' for a in fam['masters'])))
(w / 'jobs.yaml').write_text(json.dumps({'jobs': [{'reduce_sectors': reduction}, {'kira2file': {'target': [['targets']]}}]}))
paths[0].read_text()

```

[s03_run.py](s03_run.py)

The program runs counterbalanced matched trials with bounded processes and archived evidence.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def allocated(p)
def rss_tree(pid)
def limits()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

The command accepts these parser options:

- `'--pilot'`: action='store_true'.
- `'--case'`: type=int.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
p.read_text()
p.read_text(errors='replace')
pathlib.Path('/proc/%d/task/%d/children' % (p, p)).read_text()
pathlib.Path('/proc/%d/statm' % p).read_text()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s06_freeze_inputs.py](s06_freeze_inputs.py)

The program records and enforce the exact inputs and executable sources before repeated tests.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s07_audit.py](s07_audit.py)

The program checks final exports, selected identities, paths and complete trial coverage.

The module defines these callable interfaces:

```python

def vector(terms, point, p)
def main()

```

The imported project modules are `s01_common`, `s08_verify`.

This entry point uses the paths and options set in its source.

[s08_summarize.py](s08_summarize.py)

The program summarizes matched repetitions, resource outcomes and distinct cost measures.

The module defines these callable interfaces:

```python

def median(v)
def mean(v)
def geo(v)
def counter(r, key)
def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s09_plot.py](s09_plot.py)

The program plots verified matched runtime, solver work, model work and memory.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s10_native_worker.py](s10_native_worker.py)

The file provides native Kira seeding from frozen learned seed envelopes, with default fallback.

The module defines these callable interfaces:

```python

def native_selected(fam, trim, w, plan, selected)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s01_common`, `s02_worker`.

The command accepts these parser options:

- `'case'`: type=int.
- `'size'`: type=int.
- `'policy'`: The parser accepts a value..
- `'scratch'`: type=pathlib.Path.
- `'output'`: type=pathlib.Path.

These calls show the stored input and output interface:

```python

(w / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(w / 'config/kinematics.yaml').write_text(json.dumps(kin))
(w / 'targets').write_text(''.join((label(a) + '\n' for a in component)))
(w / 'masters').write_text(''.join((label(a) + '\n' for a in fam['masters'])))
(w / 'jobs.yaml').write_text(json.dumps({'jobs': [{'reduce_sectors': reduction}, {'kira2file': {'target': [['targets']]}}]}))
paths[0].read_text()

```

[s11_native_run.py](s11_native_run.py)

The program runs counterbalanced matched trials with bounded processes and archived evidence.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def allocated(p)
def rss_tree(pid)
def limits()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

```

The command accepts these parser options:

- `'--pilot'`: action='store_true'.
- `'--case'`: type=int.

These calls show the stored input and output interface:

```python

p.write_text(json.dumps(x, indent=2) + '\n')
p.read_text()
p.read_text(errors='replace')
pathlib.Path('/proc/%d/task/%d/children' % (p, p)).read_text()
pathlib.Path('/proc/%d/statm' % p).read_text()
pathlib.Path('/proc/cpuinfo').read_text()

```

[s13_native_audit.py](s13_native_audit.py)

The program checks final exports, selected identities, paths and complete trial coverage.

The module defines these callable interfaces:

```python

def vector(terms, point, p)
def main()

```

The imported project modules are `s01_common`, `s08_verify`.

These source constants locate inputs and outputs:

```python

HERE = HERE / 'native_seed'

```

This entry point uses the paths and options set in its source.

[s14_prepare_native.py](s14_prepare_native.py)

The program freezes the native seed-envelope comparison on the same seven independent bases.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

[s15_native_summary.py](s15_native_summary.py)

The program summarizes matched repetitions, resource outcomes and distinct cost measures.

The module defines these callable interfaces:

```python

def median(v)
def mean(v)
def geo(v)
def counter(r, key)
def main()

```

The imported project modules are `s01_common`.

These source constants locate inputs and outputs:

```python

HERE = HERE / 'native_seed'

```

This entry point uses the paths and options set in its source.

[s16_native_plot.py](s16_native_plot.py)

The program plots the direct native seed-envelope comparison.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s01_common`.

This entry point uses the paths and options set in its source.

## Data and supporting files

This folder contains 57 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.json`: 6 entries.

- `.json.gz`: 49 entries.

- `.o15099438.1`: 1 entries.

- `.o15099438.2`: 1 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
