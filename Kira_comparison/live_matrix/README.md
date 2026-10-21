# Elimination decisions inside Kira

This experiment connects the frozen row model to Kira’s changing coefficient matrix. Kira supplies admissible source-row operations; the model ranks them and Kira performs the exact algebra. Paired native controls measure complete time and coefficient-operation counts. Exact replay checks verify saved operations and reductions.

The scripts build the modified translation unit, freeze physical inputs, run bounded comparisons, and audit the outputs. This is an elimination-policy experiment; the combined application retains native row choices. Logs and incomplete cases remain part of its evidence.

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
| [s00_policy_server.py](s00_policy_server.py) | Score admissible live Kira row operations with the frozen reduction model. |
| [s01_live_policy.h](s01_live_policy.h) | Live symbolic forward-elimination experiment; GPL-3.0-or-later. |
| [s02_build.py](s02_build.py) | Build one changed translation unit; reuse the unchanged installed Kira objects. |
| [s03_build.sh](s03_build.sh) | Scheduler wrapper for build; its header sets the resource limits. |
| [s04_worker.py](s04_worker.py) | Run native equation generation and choose live forward operations inside Kira. |
| [s05_run.py](s05_run.py) | Counterbalanced trials with hard time, memory, scratch and output bounds. |
| [s06_run.sh](s06_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s07_audit.py](s07_audit.py) | Replay exact-operation records and verify archived native reductions. |
| [s08_summarize.py](s08_summarize.py) | Summarize complete paired trials and preserve incomplete-case counts. |
| [s09_array.sh](s09_array.sh) | Scheduler wrapper for array; its header sets the resource limits. |
| [s10_prepare.py](s10_prepare.py) | Freeze the benchmark inputs after exact pilot checks, before repeated trials. |
| [s11_plot.py](s11_plot.py) | Plot matched elapsed times and exact coefficient-operation counts. |
| [s12_finalize.sh](s12_finalize.sh) | Scheduler wrapper for finalize; its header sets the resource limits. |
| [s13_update_report.py](s13_update_report.py) | Write the measured live-matrix section and synchronize its scientific scope. |
| [s14_readmes.py](s14_readmes.py) | Document the checked live policy, controls, limits, execution and measured results. |
| [s15_build_report.sh](s15_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |

## Data and supporting files

- [COPYING](COPYING): License terms for the code in this folder.

- [KiraLiveFull.o15109182.1](KiraLiveFull.o15109182.1): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveFull.o15109182.2](KiraLiveFull.o15109182.2): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveFull.o15109182.3](KiraLiveFull.o15109182.3): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveFull.o15109182.4](KiraLiveFull.o15109182.4): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveFull.o15109182.5](KiraLiveFull.o15109182.5): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveFull.o15109182.6](KiraLiveFull.o15109182.6): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveFull.o15109182.7](KiraLiveFull.o15109182.7): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveMatrix.o15108816](KiraLiveMatrix.o15108816): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveMatrix.o15108848](KiraLiveMatrix.o15108848): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveMatrix.o15108899](KiraLiveMatrix.o15108899): Cluster job output or error log; the suffix identifies the job and array task.

- [KiraLiveMatrix.o15108900](KiraLiveMatrix.o15108900): Cluster job output or error log; the suffix identifies the job and array task.

- [audit.log](audit.log): This file records checks of the corresponding calculation.

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [build.log](build.log): This file contains saved program messages.

- [figure_values.csv](figure_values.csv): Saved figure_values.csv record for row selection inside Kira’s changing coefficient matrix; the producer code defines its fields.

- [frozen_inputs.json](frozen_inputs.json): Saved frozen_inputs.json record for row selection inside Kira’s changing coefficient matrix; the producer code defines its fields.

- [pilot_validation.json](pilot_validation.json): Recorded checks of the calculation, data, or selected settings.

- [plan.json](plan.json): Saved plan.json record for row selection inside Kira’s changing coefficient matrix; the producer code defines its fields.

- [plot.log](plot.log): This file contains saved program messages.

- [plot_review.log](plot_review.log): This file contains saved program messages.

- [report_values.json](report_values.json): Saved report_values.json record for row selection inside Kira’s changing coefficient matrix; the producer code defines its fields.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [figures](figures/README.md).

- [pilot](pilot/README.md).

- [results](results/README.md).
