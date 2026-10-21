# Source: exact sufficiency of the neural model’s selected seeds

This folder contains the code and records for exact sufficiency of the neural model’s selected seeds.

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
| [s00_check_kira.py](s00_check_kira.py) | Small exact Kira fixtures before testing predicted seed sets. |
| [s02_common.py](s02_common.py) | Frozen inputs, bounded exact rational arithmetic, and seed-filtered systems. |
| [s03_kira_adapter.py](s03_kira_adapter.py) | Export disjoint seed selections and read Kira's exact symbolic reductions. |
| [s04_run_pilot.py](s04_run_pilot.py) | Run bounded mathematical checks and representative held-out Kira reductions. |
| [s06_evaluate.py](s06_evaluate.py) | Freeze the solver protocol and evaluate disjoint held-out systems on Hoffman. |
| [s08_verify.py](s08_verify.py) | Independent finite-field checks of the symbolic coefficients exported by Kira. |
| [s09_check_import.py](s09_check_import.py) | Check supported symbolic-system import modes on the small legacy-family pilot. |
| [s11_summarize.py](s11_summarize.py) | Validates saved solver records, then summarize exact target completion. |
| [s13_plot_results.py](s13_plot_results.py) | Plot complete symbolic reductions and the selected candidate fractions. |
| [s15_update_report.py](s15_update_report.py) | Updates the scientific report from the completed Kira sufficiency test. |
| [s16_check_target_order.py](s16_check_target_order.py) | Check direct target ordering without changing seeds or source identities. |
| [s18_check_master_span.py](s18_check_master_span.py) | Test exact membership in the span of identities and specified masters. |
