# Kira timing and correctness comparisons

These records preserve development or earlier comparisons for Kira timing and correctness comparisons. They document the tested settings, including incomplete or rejected attempts.

This folder retains an earlier stage, development check or saved comparison.
Use its records to interpret that stage.
Use the current parent application for a new calculation.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Scripts

| File | Purpose |
|---|---|
| [s00_prepare.py](s00_prepare.py) | Freeze outcome-independent held-out cases, models, and resource limits. |
| [s01_common.py](s01_common.py) | Public inputs and exact coefficient arithmetic for paired Kira comparisons. |
| [s02_worker.py](s02_worker.py) | One isolated symbolic reduction, with live inference and exact fallback. |
| [s03_run.py](s03_run.py) | Run counterbalanced matched trials with bounded processes and archived evidence. |
| [s06_freeze_inputs.py](s06_freeze_inputs.py) | Records and enforce the exact inputs and executable sources before repeated tests. |
| [s07_audit.py](s07_audit.py) | Check final exports, selected identities, paths and complete trial coverage. |
| [s08_summarize.py](s08_summarize.py) | Summarize matched repetitions, resource outcomes and distinct cost measures. |
| [s09_plot.py](s09_plot.py) | Plot verified matched runtime, solver work, model work and memory. |
| [s10_native_worker.py](s10_native_worker.py) | Native Kira seeding from frozen learned seed envelopes, with default fallback. |
| [s11_native_run.py](s11_native_run.py) | Run counterbalanced matched trials with bounded processes and archived evidence. |
| [s13_native_audit.py](s13_native_audit.py) | Check final exports, selected identities, paths and complete trial coverage. |
| [s14_prepare_native.py](s14_prepare_native.py) | Freeze the native seed-envelope comparison on the same seven independent bases. |
| [s15_native_summary.py](s15_native_summary.py) | Summarize matched repetitions, resource outcomes and distinct cost measures. |
| [s16_native_plot.py](s16_native_plot.py) | Plot the direct native seed-envelope comparison. |

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
