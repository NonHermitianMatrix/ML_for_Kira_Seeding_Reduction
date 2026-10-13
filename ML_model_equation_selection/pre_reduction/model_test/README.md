# model test

This folder contains reserved test inputs, outputs or checks.
Keep these records outside model fitting and threshold selection.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../README.md).

## Data and supporting files

- [audit.json](audit.json): This file records checks of the corresponding calculation.

- [complete.json](complete.json): This file contains structured records from the parent calculation.

- [document_values.json](document_values.json): This file contains structured records from the parent calculation.

- [release_check.json](release_check.json): This file records checks of the corresponding calculation.

- [resume_metadata.json](resume_metadata.json): This file records the family, generation bounds and validation information.

- [scheduler_accounting.json](scheduler_accounting.json): This file contains structured records from the parent calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

## Child folders

- [inputs](inputs/README.md).

- [integration](integration/README.md).

- [interrupted](interrupted/README.md).

- [plots](plots/README.md).

- [results](results/README.md).
