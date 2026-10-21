# cumulative speedup

This folder compares three complete reductions of the restricted vacuum family.
The methods use the saved original Kira, the later full-pool control and the specialized recurrence method.
Every method receives the same targets, mass profiles and loop orders.
All 120 measured workflows pass exact checks.
The geometric mean speedup is 543.815 relative to the original control.
This result includes exact recurrence reuse and implementation changes.
It is not an isolated machine learning gain.

`s01_cases.py` defines eight groups with three mass profiles each.
Each group requests loop orders one through twelve.
`s02_worker.py` runs one complete request.
`s03_study.py` controls preparation, freezing and tests.
`s10_parallel.py` assigns matched groups to four scheduled CPU slots.

Use the scheduler wrapper with four slots and distinct cores:

```bash
qsub -pe shared 4 -binding env linear:4 Kira_comparison/cumulative_speedup/s04_run.sh pipeline
```

This command repeats a completed study.
Use it only for a deliberate new reproduction.
Keep the existing results and freeze record.
Each worker has a 2,400 MiB address-space limit and a 1,200-second limit.
Each worker has a 64 MiB scratch limit.
Complete time includes fresh-process startup, input, identities, exact algebra, checks, output writing and output reading.
Queue waiting, offline training and the later independent audit remain outside the timer.

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
| [s00_cumulative.py](s00_cumulative.py) | Shared paths, frozen provenance, bounded resources and coefficient output. |
| [s01_cases.py](s01_cases.py) | Declares independent matched requests without fitting any policy. |
| [s02_worker.py](s02_worker.py) | Run a complete matched reduction and save lossless exact coefficients. |
| [s03_study.py](s03_study.py) | Executes paired frozen comparisons with resource monitoring. |
| [s04_run.sh](s04_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s05_audit.py](s05_audit.py) | Audit every saved coefficient, paired input system and frozen dependency. |
| [s06_analyze.py](s06_analyze.py) | Reports direct cumulative ratios and absolute times on the same cases. |
| [s07_plot.py](s07_plot.py) | Create standalone scientific plots of the direct cumulative comparison. |
| [s08_document.py](s08_document.py) | Write measured cumulative results into the scientific report and READMEs. |
| [s09_finish.sh](s09_finish.sh) | Scheduler wrapper for finish; its header sets the resource limits. |
| [s10_parallel.py](s10_parallel.py) | Run independent paired groups on four explicitly allocated physical cores. |

## Data and supporting files

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

- [protocol.json](protocol.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [report_build.log](report_build.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for exact vacuum recurrence compared with supplied-equation Kira; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [development](development/README.md).

- [objects](objects/README.md).

- [pilot](pilot/README.md).

- [test](test/README.md).
