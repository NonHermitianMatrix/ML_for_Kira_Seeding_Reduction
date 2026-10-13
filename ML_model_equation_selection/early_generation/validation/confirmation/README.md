# confirmation

This folder contains reserved test inputs, outputs or checks.
Keep these records outside model fitting and threshold selection.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../../README.md).

## Data and supporting files

This folder contains 84 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.001_r0.json.gz`: 2 entries.

- `.001_r1.json.gz`: 2 entries.

- `.001_r2.json.gz`: 2 entries.

- `.003_r0.json.gz`: 3 entries.

- `.003_r1.json.gz`: 3 entries.

- `.003_r2.json.gz`: 3 entries.

- `.01_r0.json.gz`: 9 entries.

- `.01_r1.json.gz`: 9 entries.

- `.01_r2.json.gz`: 9 entries.

- `.json.gz`: 42 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
