# model test

This folder contains reserved test inputs, outputs or checks.
Keep these records outside model fitting and threshold selection.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../README.md).

## Data and supporting files

This folder contains 286 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.001_r0.json.gz`: 14 entries.

- `.001_r1.json.gz`: 14 entries.

- `.001_r2.json.gz`: 14 entries.

- `.001_r3.json.gz`: 14 entries.

- `.001_r4.json.gz`: 14 entries.

- `.json`: 6 entries.

- `.json.gz`: 210 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.

## Child folders

- [application](application/README.md).

- [composition](composition/README.md).

- [confirmation](confirmation/README.md).

- [labels](labels/README.md).

- [plots](plots/README.md).
