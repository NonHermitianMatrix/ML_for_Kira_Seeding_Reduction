# Cost of parallel prediction during Kira reduction

This folder contains the code and records for cost of parallel prediction during Kira reduction.

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
| [reduction_parallel.patch](reduction_parallel.patch) | This patch records changes to the native Kira source. |
| [s00_check_arithmetic.cpp](s00_check_arithmetic.cpp) | Exact checks for field inversion and all source-row features. |
| [s01_check_seed.py](s01_check_seed.py) | Check bitwise probabilities and masks against the preceding compiled network. |

## Data and supporting files

- [adoption.json](adoption.json): Saved adoption.json record for cost of parallel prediction during Kira reduction; the producer code defines its fields.

- [application_verification.json](application_verification.json): This file records checks of the corresponding calculation.

- [arithmetic_check.json](arithmetic_check.json): This file records checks of the corresponding calculation.

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [confirmation_summary.json](confirmation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [release.json](release.json): Saved release.json record for cost of parallel prediction during Kira reduction; the producer code defines its fields.

- [report_values.json](report_values.json): Saved report_values.json record for cost of parallel prediction during Kira reduction; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [seed_parity.json](seed_parity.json): Saved seed_parity.json record for cost of parallel prediction during Kira reduction; the producer code defines its fields.

- [validation_summary.json](validation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [application_checks](application_checks/README.md).

- [attempts](attempts/README.md).

- [confirmation](confirmation/README.md).

- [rejected_euclid](rejected_euclid/README.md).

- [shared](shared/README.md).

- [validation](validation/README.md).
