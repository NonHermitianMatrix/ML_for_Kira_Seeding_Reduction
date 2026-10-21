# Extra 20 epochs: selection of IBP seeds

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
| [s00_continue.py](s00_continue.py) | Continues the published seed checkpoint for the requested twenty epochs. |
| [s01_run.sh](s01_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |

## Data and supporting files

- [jobs.json](jobs.json): Saved jobs.json record for selection of IBP seeds; the producer code defines its fields.

- [launch.json](launch.json): Saved launch.json record for selection of IBP seeds; the producer code defines its fields.

- [preflight.json](preflight.json): Saved preflight.json record for selection of IBP seeds; the producer code defines its fields.

- [request.json](request.json): Physical inputs and target lists for the recorded experiment.

- [run.lock](run.lock): Saved run.lock record for selection of IBP seeds; the producer code defines its fields.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [setup_validation.json](setup_validation.json): Recorded checks of the calculation, data, or selected settings.

- [status.json](status.json): This file records the execution state.
