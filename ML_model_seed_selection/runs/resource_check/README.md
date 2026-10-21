# Resource check: selection of IBP seeds

This folder contains the code and records for selection of IBP seeds.

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
| [s00_cpu_scaling.py](s00_cpu_scaling.py) | Measures CPU scaling using training records; never change production weights. |
| [s01_run_cpu_scaling.sh](s01_run_cpu_scaling.sh) | Scheduler wrapper for run cpu scaling; its header sets the resource limits. |
| [s02_end_to_end_scaling.py](s02_end_to_end_scaling.py) | Compare full training-input and gradient work with one and two CPU threads. |
| [s03_run_end_to_end.sh](s03_run_end_to_end.sh) | Scheduler wrapper for run end to end; its header sets the resource limits. |

## Data and supporting files

- [cpu_scaling.json](cpu_scaling.json): Saved cpu_scaling.json record for selection of IBP seeds; the producer code defines its fields.

- [decision.json](decision.json): Saved decision.json record for selection of IBP seeds; the producer code defines its fields.

- [end_to_end.log](end_to_end.log): This file contains saved program messages.

- [end_to_end_scaling.json](end_to_end_scaling.json): Saved end_to_end_scaling.json record for selection of IBP seeds; the producer code defines its fields.

- [scheduler.log](scheduler.log): This file contains saved program messages.
