# Master basis for one integral family

This folder defines the family and its retained master integrals. Its directory name is the family identifier used by the collection reader.

- [definition.json](definition.json): loop and external momenta, propagators, scalar products, and sectors.
- [masters.json](masters.json): master identifiers and their integral index vectors.
- [masters.txt](masters.txt): the master index list in plain text.

Use the same family directory name in [target_integrals](../../../target_integrals/README.md) and [master_to_target](../../../master_to_target/README.md). The latter stores target coefficients and reduction steps.

[The collection reader](../../../README.md) accepts `--family FAMILY --kind masters` or `--kind definition`. Master identifiers are local to their family.
