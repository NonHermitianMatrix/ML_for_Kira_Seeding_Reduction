# seed threshold training

This folder contains training inputs or saved training results.
Keep the stored family division unchanged.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../README.md).

## Data and supporting files

This folder contains 96 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.003.json.gz`: 12 entries.

- `.01.json.gz`: 12 entries.

- `.03.json.gz`: 12 entries.

- `.1.json.gz`: 12 entries.

- `.3.json.gz`: 12 entries.

- `.5.json.gz`: 12 entries.

- `.json.gz`: 24 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
