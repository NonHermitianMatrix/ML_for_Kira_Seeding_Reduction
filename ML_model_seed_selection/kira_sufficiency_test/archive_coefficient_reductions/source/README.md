# source

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

[s00_check_kira.py](s00_check_kira.py)

The file provides small exact Kira fixtures before testing predicted seed sets.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORK = ROOT / '.tools/kira-seed-sufficiency'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'fixture_runs.json').write_text(json.dumps(results, indent=2) + '\n')
(w / 'system.kira').write_text(system + '\n')
(w / 'targets').write_text('\n'.join(selected) + '\n')
(w / 'masters').write_text('\n'.join(masters) + '\n')
p.read_text(errors='replace')
(w / 'run.log').read_text(errors='replace')

```

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
def export(family, blocks, w)
def run_once(w, timeout=600, scratch_limit=67108864)
def run_kira(w, timeout=600, scratch_limit=67108864)
def parse_output(path)
def assess(family, manifest, output, reference_by_id)

```

The imported project modules are `s02_common`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'targets').write_text(''.join(('%d\n' % i for i in targetmap)))
(w / 'masters').write_text(''.join(('%d\n' % i for i in basis)))
(w / 'jobs.yaml').write_text(JOBS)
(w / 'run.log').read_text(errors='replace')

```

[s04_run_pilot.py](s04_run_pilot.py)

The program runs bounded mathematical checks and representative held-out Kira reductions.

The module defines these callable interfaces:

```python

def arithmetic_checks()
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s03_kira_adapter`, `s06_evaluate`, `s08_verify`.

This entry point uses the paths and options set in its source.

[s06_evaluate.py](s06_evaluate.py)

The program freezes the solver protocol and evaluate disjoint held-out systems on Hoffman.

The module defines these callable interfaces:

```python

def protocol()
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

```

Import this helper module from the stage that uses it.

[s09_check_import.py](s09_check_import.py)

The program checks supported symbolic-system import modes on the small legacy-family pilot.

The imported project modules are `s03_kira_adapter`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'system.kira').read_text()
(w / 'system.kira').write_text(content)
(w / 'jobs.yaml').write_text(JOBS.replace('otf: false', 'otf: true'))

```

[s11_summarize.py](s11_summarize.py)

The program validates saved solver records, then summarize exact target completion.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s06_evaluate`.

This entry point uses the paths and options set in its source.

[s13_plot_results.py](s13_plot_results.py)

The program plots complete symbolic reductions and the selected candidate fractions.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`, `numpy`.

The imported project modules are `s02_common`.

This entry point uses the paths and options set in its source.

[s15_update_report.py](s15_update_report.py)

The program updates the scientific report from the completed Kira sufficiency test.

The module defines these callable interfaces:

```python

def main(commit)

```

The imported project modules are `s02_common`.

The command accepts these parser options:

- `'--data-commit'`: required=True.

These calls show the stored input and output interface:

```python

main.read_text()
(out / 'seed_kira_test.tex').write_text(METHOD + results)
p.read_text()
p.write_text(text)
main.write_text(s)
bib.read_text()
bib.write_text(text)

```

[s16_check_target_order.py](s16_check_target_order.py)

The program checks direct target ordering without changing seeds or source identities.

The imported project modules are `s03_kira_adapter`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'system.kira').write_text('\n'.join(lines) + '\n')
(w / 'masters').write_text(''.join((str(permutation[i]) + '\n' for i in oldmasters)))
(w / 'targets').write_text(''.join((str(permutation[i]) + '\n' for i in oldtargets)))
(w / 'system.kira').read_text()

```

[s18_check_master_span.py](s18_check_master_span.py)

The program tests exact membership in the span of identities and specified masters.

The imported project modules are `s03_kira_adapter`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(w / 'masters').read_text()

```

