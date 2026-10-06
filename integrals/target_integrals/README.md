# Target integrals

This folder contains 381,272 targets in 2,100 families: 85,732 individual integrals and 295,540 integral expressions. Each families/<family-id>/inputs.jsonl.gz file contains one JSON record per target. A record gives the target ID, family ID, kind, ordered symbolic terms, sampled modular coefficients and links to the corresponding master and reduction files.

The added 1,100 vacuum families supply 128 targets each, or 140,800 targets. An expression contains up to three scalar roots with rational coefficients that can depend on the dimension and common squared-mass scale. The scale powers make all terms have the same mass dimension. Exact master combinations and inverse identity steps construct these targets.

The fixed model division contains 266,890 training targets in 1,463 families and 114,382 test targets in 637 families. [Training](../training/README.md) and [testing](../testing/README.md) contain separate linked views of these canonical files. A target always keeps its complete candidate list and reference records in the same division. Related new mass profiles stay together across loop orders.

[The catalog](../catalog.json) identifies every target file. Match the target ID with [master_to_target](../master_to_target/README.md) to obtain master coefficients, seeds, construction records and forward traces. The stored path is a checked sufficient reduction; its global minimality is not established. [The generation method](../higher_loops/README.md) gives the family bounds and checks.
