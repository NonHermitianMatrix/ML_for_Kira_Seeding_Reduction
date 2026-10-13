# fixed pool

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

[s04_optimal_paths.py](s04_optimal_paths.py)

The program certifies minimum counted field operations over every admissible finite pivot path.

The module defines these callable interfaces:

```python

def systems()
def certificate(system)
def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'optimal_paths/summary.json').write_text(json.dumps(summaries, indent=2) + '\n')
pathlib.Path(__file__).read_bytes()

```

[s05_verify_certificates.py](s05_verify_certificates.py)

The program checks every certificate edge independently using exact symbolic matrices.

The module defines these callable interfaces:

```python

def verify(p)
def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'optimal_paths/verification.json').write_text(json.dumps(dict(success=True, systems=results), indent=2) + '\n')

```

## Data and supporting files

- [massive_tadpole.json.gz](massive_tadpole.json.gz): This file contains structured records from the parent calculation.

- [massless_bubble.json.gz](massless_bubble.json.gz): This file contains structured records from the parent calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [verification.json](verification.json): This file records the independent checks.
