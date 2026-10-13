# Study progress logs

These files contain scheduler progress, stage results and completion messages.
`study.log` records the first job, which stopped during validation for a Git cache storage correction.
`resumed.log` records the job that reused completed records and repeated the unfinished calculation.
`analysis.log` records the independent summary and figure job.
The stop did not interrupt any reserved timing calculation.

Use the job scripts in [the parent guide](../README.md).
Use the saved scientific records, rather than log text, to reproduce the result tables.

`figure_check.log` records the repeated figure check after correcting label placement.
The repeated analysis does not rerun training or reductions.
