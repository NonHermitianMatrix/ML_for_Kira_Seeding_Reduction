# Reference reductions and construction records

These records connect this family’s target expressions to its master basis. Match the target `id` across the input, reference, and elimination trace. Match each reference master ID to the family’s master list.

- [candidate_seeds.json](candidate_seeds.json): candidate integral indices from which IBP identities are generated.
- [construction_proofs.jsonl.gz](construction_proofs.jsonl.gz): recorded identities used to construct targets from master expansions.
- [elimination_traces.jsonl.gz](elimination_traces.jsonl.gz): allowed operations, selected pivots, coefficient changes, and operation counts.
- [generation_records.tar.gz](generation_records.tar.gz): archived records of the generation procedure.
- [identities.jsonl.gz](identities.jsonl.gz): source equations between integrals.
- [manifest.json](manifest.json): record locations and identifiers.
- [metadata.json](metadata.json): family information, generation bounds, and validation metadata.
- [references.jsonl.gz](references.jsonl.gz): target IDs, required master IDs, and exact coefficients.
- [symmetries.json](symmetries.json): index mappings that preserve the family.

The recorded path is a sufficient reduction. Its operation count is not a proof of minimum cost. Partial-fraction identities have no IBP seed label.

Use the same family directory name in [master_integrals](../../../master_integrals/README.md) and [target_integrals](../../../target_integrals/README.md). [The collection reader](../../../README.md) joins the records with `--target FAMILY:ID` and streams their compressed files.
