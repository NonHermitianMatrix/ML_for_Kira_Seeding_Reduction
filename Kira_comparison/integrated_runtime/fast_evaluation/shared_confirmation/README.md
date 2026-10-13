# shared confirmation

This folder contains reserved test inputs, outputs or checks.
Keep these records outside model fitting and threshold selection.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../README.md).

## Data and supporting files

This folder contains 800 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.json.gz`: 800 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
