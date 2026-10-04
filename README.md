# ML_for_Kira_Seeding_Reduction

This project studies System 1 models for seed selection and elimination ordering in Kira IBP reduction.

The validated collection contains 1,000 families, 9,678 master-integral entries and 240,088 targets. The targets comprise 55,384 individual integrals and 184,704 integral expressions.

The added 984 families have distinct mass and kinematic conditions for one-loop four-propagator integrals. Together with the original collection, the data cover 997 one-loop and three two-loop families. Master counts are per family; related lower-sector integrals can occur in several bases.

[Expanded collection and methods](Expanded_Integrals/README.md) describes the data, exact checks and limits. The [combined catalog](Expanded_Integrals/catalog.json) gives every family's master and target counts, and [splits.json](Expanded_Integrals/splits.json) defines the training, validation and test targets.

The initial master bases remain in [Master_Integrals](Master_Integrals/README.md), and the initial target records remain in [master_to_target](master_to_target/README.md). Each added family has a compressed archive under Expanded_Integrals/families containing its full master and target data, source equations, seed records, reduction steps and validation records. The archive reader streams these files directly on Hoffman.

Read the [report PDF](report/report.pdf), [LaTeX source](report/report.tex), [bibliography](report/references.bib) and [project rules](rules.md). Model training and performance measurements remain subsequent stages. The recorded reductions are valid reference paths; minimum seed sets and operation counts have not been established.

The primary working directory is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction on Hoffman. Generated data stay on Hoffman and GitHub, with no local dataset copies. Tool binaries, caches, temporary engine state and scheduler logs stay outside Git. The total project storage ceiling is 10 GB.
