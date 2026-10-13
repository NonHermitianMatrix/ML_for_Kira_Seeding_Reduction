# worker 00

This folder supports the calculation described in the parent guide.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../../README.md).

## Data and supporting files

This folder contains 1836 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.gz`: 4 entries.

- `.json.gz`: 754 entries.

- `.kira.gz`: 752 entries.

- `.log.gz`: 2 entries.

- `.summary.json.gz`: 322 entries.

- `.yaml.gz`: 2 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
