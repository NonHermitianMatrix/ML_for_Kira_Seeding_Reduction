# shared

This folder stores shared calculation records.
Read each record through the parent stage reader.
The reader restores referenced objects and checks their content.

Read [the parent guide](../README.md) for the stage and data flow.

The producing and reading code is described in [the stage guide](../README.md).

## Data and supporting files

This folder contains 458 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.json.gz`: 458 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
