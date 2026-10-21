# Target expressions for one integral family

[inputs.jsonl.xz](inputs.jsonl.xz) contains one target record per line. A target can be an individual integral or a linear combination. Its `id` connects the expression to its exact reference and recorded reduction trace.

The directory name identifies the family. Use the same name in [master_integrals](../../../master_integrals/README.md) for propagators and the basis, and in [master_to_target](../../../master_to_target/README.md) for coefficients, seeds, and identities.

[The collection reader](../../../README.md) accepts `--family FAMILY --kind inputs --limit 1`. Its `--target FAMILY:ID` option joins the matching records. It streams gzip or xz data without expanding the full file.
