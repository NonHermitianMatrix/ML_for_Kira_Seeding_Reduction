# Relations between masters and targets

This folder connects every target to its exact master expansion and the identities used to construct and reduce it. Its records cover 381,272 targets, 3,568,907 source equations and 2,206,660 recorded elimination steps across 2,100 families.

Each families/<family-id>/ folder supplies references.jsonl.gz, identities.jsonl.gz, elimination_traces.jsonl.gz and candidate_seeds.json. Reference records contain target and master IDs, exact rational coefficients, the sufficient IBP seed set, source-equation IDs, three finite-field samples and arithmetic counts. Each trace gives allowed equations, the chosen pivot and source, coefficients before and after each operation, the final master row and operation counts.

The added vacuum families also supply construction_proofs.jsonl.gz and scalar_proofs.jsonl.gz. These retain the exact reverse construction from master combinations and the scalar relations used to form each target. metadata.json documents the domain; manifest.json records file sizes and hashes. symmetries.json states the available symmetry information.

IBP source rows record their actual seeds and derivative operators. Algebraic mass partial-fraction rows carry no IBP seed. Reference seed sets consist of the IBP seeds used by the recorded forward path. The path uses a stated local choice rule; the records do not prove a globally smallest seed set or shortest reduction.

[The catalog](../catalog.json) joins these files to [masters](../master_integrals/README.md) and [targets](../target_integrals/README.md). [The current audit](../validation_summary.json) checks all family manifests and cross-folder links, and preserves separate evidence for the original mathematical checks and [the added higher-loop checks](../higher_loops/validation.json). The training and testing manifests define current assignments, including for older records with historical split labels.
