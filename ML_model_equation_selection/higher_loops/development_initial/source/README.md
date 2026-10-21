# Source: restricted vacuum reductions across loop orders

This folder contains the code and records for restricted vacuum reductions across loop orders.

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
| [s00_math.py](s00_math.py) | Exact restricted vacuum identities and coefficient-free dependency choices. |
| [s01_train.py](s01_train.py) | Train small equation-choice trees from exact dependency counts. |
| [s02_reduce.py](s02_reduce.py) | Generate a sufficient equation system, run bounded Kira and check exact coefficients. |
| [s03_cases.py](s03_cases.py) | Create distinct mass profiles and exponent batches before fitting or timing. |
| [s04_study.py](s04_study.py) | Run predeclared comparisons in sequential bounded worker processes. |
| [s06_select.py](s06_select.py) | Chooses policies on validation measurements and freeze before reserved tests. |
| [s07_analyze.py](s07_analyze.py) | Audit exact test exports and summarize the frozen paired costs. |
| [s08_application.py](s08_application.py) | Applies the frozen higher-loop deployment to a new supported family request. |
| [s09_plot.py](s09_plot.py) | Makes standalone figures from the frozen higher-loop cost audit. |
| [s10_polynomial.py](s10_polynomial.py) | Bounded exact reading of Kira's univariate rational coefficients. |
| [s11_reader_audit.py](s11_reader_audit.py) | Cross-checks a fast exact coefficient reader against symbolic algebra. |
| [s14_extrapolate.py](s14_extrapolate.py) | Check the frozen application at additional loop orders above the timing set. |
