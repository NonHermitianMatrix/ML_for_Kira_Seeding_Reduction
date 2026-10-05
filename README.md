# ML_for_Kira_Seeding_Reduction

This project studies System 1 models for seed selection and elimination ordering in Kira IBP reduction.

All integral data are organized under [integrals](integrals/README.md). The collection contains 1,000 families, 9,678 master entries and 240,472 targets. The targets comprise 55,768 individual integrals and 184,704 integral expressions.

[master_integrals](integrals/master_integrals/README.md) contains every stored master basis and its family definition. [target_integrals](integrals/target_integrals/README.md) contains every target. [master_to_target](integrals/master_to_target/README.md) links the targets to their exact master expansions, seeds, identities, construction steps, elimination steps and operation counts.

The collection covers 997 one-loop families and three two-loop families. The added 984 families use different exact mass and kinematic conditions for one-loop four-propagator integrals. Master counts are per family, so related lower-sector integrals can occur in several bases. The recorded paths give valid reductions; minimum seed sets and operation counts remain unproved.

The [combined catalog](integrals/catalog.json) gives the family counts and file locations. The collection's original [split file](integrals/splits.json) defines 198,527 training targets, 19,600 validation targets and 22,345 test targets. The seed model uses its own grouped 70:30 split for the authorized training run.

The [seed-selection model](ML_model_seed_selection/README.md) has completed training and held-out testing. Its separate grouped 70:30 split contains 168,330 training targets and 72,142 test targets. The model scores each candidate seed using the target terms, their symbolic coefficients and ordered term pairs. Training reads the separate training view. The held-out test results and six figures are in ML_model_seed_selection/model_test/. Sections 7 and 8 of the report explain the model and its test results.

Read the [report PDF](report/report.pdf), [LaTeX source](report/report.tex), [bibliography](report/references.bib) and [project rules](rules.md). The report's dataset citations identify preserved Git commits, so the documented calculations remain accessible after this directory change.

The primary working directory is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction on Hoffman. Generated datasets stay on Hoffman and GitHub. The total project storage ceiling is 10 GB, including tools, caches, temporary files and Git history.

<!-- seed-training-status:start -->
The seed-selection model completed ten training passes and the held-out test on 72,142 targets. Its [test results and graphs](ML_model_seed_selection/model_test/README.md) report 95.734% seed precision, 94.112% recall and 81.916% exact reference-set agreement. The [report](report/report.pdf) includes the results and the lower performance of the single held-out two-loop family.
<!-- seed-training-status:end -->

The [reduction-propagation model](ML_model_reduction/README.md) ranks the next exact row operation from a supplied list and returns its estimated confidence. It completed ten passes on 455,341 choice states from 693 families, using the same grouped training families as the seed model. Section 9 of the report defines the matrix input, action probabilities and reference-choice training. Completed training details are recorded in ML_model_reduction/trained_model.json; completed held-out results appear in [model_test/](ML_model_reduction/model_test/README.md) and Section 10 of the report.

<!-- reduction-test:start -->
The frozen reduction model was tested on 72,142 targets in 307 held-out families. It matched 95.469% of recorded choices on 194,347 states with at least two actions. Complete learned paths matched all three sampled master expansions for 72,026 targets; the fixed local rule passed 71,463. Mean attempted reduction times were 8.4426 ms and 0.4262 ms, respectively. Reference paths are valid without a proof of minimality. These are target-row tests; no full Kira speedup was measured.
<!-- reduction-test:end -->
