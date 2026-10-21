# Reference reductions and construction records

These records connect this family’s target expressions to its master basis. Match the target `id` across the input, reference, and elimination trace. Match each reference master ID to the family’s master list.

- [candidate_seeds.json](candidate_seeds.json): candidate integral indices from which IBP identities are generated.
- [construction_proofs.jsonl.xz](construction_proofs.jsonl.xz): recorded identities used to construct targets from master expansions.
- [elimination_traces.jsonl.xz](elimination_traces.jsonl.xz): allowed operations, selected pivots, coefficient changes, and operation counts.
- [identities.jsonl.xz](identities.jsonl.xz): source equations between integrals.
- [manifest.json](manifest.json): record locations and identifiers.
- [metadata.json](metadata.json): family information, generation bounds, and validation metadata.
- [references.jsonl.xz](references.jsonl.xz): target IDs, required master IDs, and exact coefficients.
- [scalar_proofs.jsonl.xz](scalar_proofs.jsonl.xz): construction checks for individual target integrals.
- [symmetries.json](symmetries.json): index mappings that preserve the family.

The recorded path is a sufficient reduction. Its operation count is not a proof of minimum cost. Partial-fraction identities have no IBP seed label.

Use the same family directory name in [master_integrals](../../../master_integrals/README.md) and [target_integrals](../../../target_integrals/README.md). [The collection reader](../../../README.md) joins the records with `--target FAMILY:ID` and streams their compressed files.
