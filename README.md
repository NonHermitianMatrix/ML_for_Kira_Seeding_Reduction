# ML_for_Kira_Seeding_Reduction

This project studies System 1 models for seed selection and elimination ordering in Kira IBP reduction.

All integral data are organized under [integrals](integrals/README.md). The collection contains 1,000 families, 9,678 master entries and 240,472 targets. The targets comprise 55,768 individual integrals and 184,704 integral expressions.

[master_integrals](integrals/master_integrals/README.md) contains every stored master basis and its family definition. [target_integrals](integrals/target_integrals/README.md) contains every target. [master_to_target](integrals/master_to_target/README.md) links the targets to their exact master expansions, seeds, identities, construction steps, elimination steps and operation counts.

The collection covers 997 one-loop families and three two-loop families. The added 984 families use different exact mass and kinematic conditions for one-loop four-propagator integrals. Master counts are per family, so related lower-sector integrals can occur in several bases. The recorded paths give valid reductions; minimum seed sets and operation counts remain unproved.

The [combined catalog](integrals/catalog.json) gives the family counts and file locations. The collection's original [split file](integrals/splits.json) defines 198,527 training targets, 19,600 validation targets and 22,345 test targets. The seed model uses its own grouped 70:30 split for the authorized training run.

The [seed-selection model](ML_model_seed_selection/README.md) is implemented and training is authorized. Its separate grouped 70:30 split contains 168,330 training targets and 72,142 test targets. The model scores each candidate seed using the target terms, their symbolic coefficients and ordered term pairs. Training reads the separate training view. Held-out model testing remains deferred. Section 7 of the report explains the model.

Read the [report PDF](report/report.pdf), [LaTeX source](report/report.tex), [bibliography](report/references.bib) and [project rules](rules.md). The report's dataset citations identify preserved Git commits, so the documented calculations remain accessible after this directory change.

The primary working directory is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction on Hoffman. Generated datasets stay on Hoffman and GitHub. The total project storage ceiling is 10 GB, including tools, caches, temporary files and Git history.

<!-- seed-training-status:start -->
The seed-selection model completed ten training epochs. Its [trained weights](ML_model_seed_selection/trained_model.pt) and [training metadata](ML_model_seed_selection/trained_model.json) are stored in the model folder. The held-out test set remains unused for model evaluation.
<!-- seed-training-status:end -->
