# Fixed pool: transfer to scattering structures and symbolic kinematics

This folder contains the code and records for transfer to scattering structures and symbolic kinematics.

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
| [s04_optimal_paths.py](s04_optimal_paths.py) | Certifies minimum counted field operations over every admissible finite pivot path. |
| [s05_verify_certificates.py](s05_verify_certificates.py) | Check every certificate edge independently using exact symbolic matrices. |

## Data and supporting files

- [massive_tadpole.json.gz](massive_tadpole.json.gz): Saved massive_tadpole.json.gz record for transfer to scattering structures and symbolic kinematics; the producer code defines its fields.

- [massless_bubble.json.gz](massless_bubble.json.gz): Saved massless_bubble.json.gz record for transfer to scattering structures and symbolic kinematics; the producer code defines its fields.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [verification.json](verification.json): This file records the independent checks.
