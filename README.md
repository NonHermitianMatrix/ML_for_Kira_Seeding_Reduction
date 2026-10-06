# ML for Kira seed selection and reduction

This project studies lightweight models for selecting IBP seeds and allowed elimination steps while exact arithmetic retains responsibility for the reductions.

The [integral collection](integrals/README.md) contains 2,100 family instances, 12,967 family-local master entries and 381,272 targets. It includes 997 one-loop families, 103 two-loop families and 100 families at every order from three through twelve. The added families are 100 mass profiles per loop order for restricted coupled vacuum integrals. Their analytic bases, Euler IBP and mass partial-fraction identities give exact reverse constructions. The profiles share a small set of graph structures; the collection does not represent arbitrary high-loop scattering integrals.

[master_integrals/](integrals/master_integrals/README.md) stores definitions and bases; [target_integrals/](integrals/target_integrals/README.md) stores targets; [master_to_target/](integrals/master_to_target/README.md) stores master expansions, seeds, equations, constructions, elimination traces and operation counts. Matching IDs connect all records. [higher_loops/](integrals/higher_loops/README.md) documents the new mathematical domain and independent checks.

The grouped split gives 266,890 training targets in 1,463 families and 114,382 test targets in 637 families. Related added mass profiles remain together across loop orders, and prior assignments remain fixed. The separate [training](integrals/training/README.md) and [testing](integrals/testing/README.md) views link to canonical data without copying it. Shared lower-sector physics can occur across profiles.

Both the [seed model](ML_model_seed_selection/README.md) and [reduction model](ML_model_reduction/README.md) completed twenty new passes over the expanded training set, starting from their saved weights and optimizer states. Their previous progress remains recorded separately. Frozen expanded-data testing is the next stage; earlier test artifacts remain in each model_test/archive_before_all_loops/ folder. The current report still describes the preceding tests until the new evaluation and report update finish.

The [report PDF](report/report.pdf), [LaTeX source](report/report.tex), [bibliography](report/references.bib) and [rules](rules.md) accompany the project. Hoffman is the primary working location. Generated integral data, encoded examples, trained models and tests stay on Hoffman and GitHub; only report files are also synchronized locally. The combined storage ceiling is 10 GB.
