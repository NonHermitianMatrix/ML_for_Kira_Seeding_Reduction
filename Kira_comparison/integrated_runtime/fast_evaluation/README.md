# Fast evaluation: integration of learned choices with native Kira calculations

This folder contains the code and records for integration of learned choices with native Kira calculations.

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
| [reduction_shared.patch](reduction_shared.patch) | This patch records changes to the native Kira source. |
| [s00_check_pairs.cpp](s00_check_pairs.cpp) | Compare all six modular features with the original ordered-pair calculation. |
| [s01_check_seed.py](s01_check_seed.py) | Check bitwise probabilities and masks against the preceding compiled network. |
| [s02_initial_freeze_generator.py](s02_initial_freeze_generator.py) | Freeze implementation-only changes after exact and timing validation. |

## Data and supporting files

- [adoption.json](adoption.json): Saved adoption.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [adoption_initial.json](adoption_initial.json): Saved adoption_initial.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [application_verification.json](application_verification.json): This file records checks of the corresponding calculation.

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [confirmation_summary.json](confirmation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [freeze_initial.json](freeze_initial.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [release.json](release.json): Saved release.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [report_values.json](report_values.json): Saved report_values.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [row_feature_check.json](row_feature_check.json): This file records checks of the corresponding calculation.

- [seed_parity.json](seed_parity.json): Saved seed_parity.json record for integration of learned choices with native Kira calculations; the producer code defines its fields.

- [validation_summary.json](validation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [shared_application_checks](shared_application_checks/README.md).

- [shared_confirmation](shared_confirmation/README.md).

- [shared_validation](shared_validation/README.md).
