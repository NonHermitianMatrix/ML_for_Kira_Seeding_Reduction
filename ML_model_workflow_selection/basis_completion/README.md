# Basis completion and selective seed expansion

This study tests smaller Kira reductions. It can reduce targets to temporary basis integrals and then reduce those integrals to the required masters. It also tests changes to individual seed limits. Every final result must use the prescribed basis.

The code requires Python 3.9, NumPy, SymPy, Matplotlib, the existing Kira and Fermat executables, and the Hoffman scheduler. The report build also requires the existing Tectonic installation. Keep the preceding [graph-specific study](../type_specialists/README.md) and its frozen models available; this route calls them for its baseline and fallback.

Use the scientific Python environment at `.tools/seed-model/venv/bin/python`. Run the code from the repository root on a scheduled Hoffman compute node. Keep one study job active. The retained file limit is 16 MiB. Each Kira process uses one CPU and at most 32 MiB of temporary files. The process-tree memory limit is 2100 MiB.

- `s00_native.py` runs bounded exact Kira reductions. It can allow an intermediate basis when the caller requests it.
- `s01_workflow.py` makes inputs, reduces temporary masters, combines exact coefficients, checks the final basis, and calls the previous frozen route if a new strategy fails.
- `s02_job.sh` supplies the scheduler and memory settings.
- `s03_probe.py` tests candidate strategies on development profile 71. It writes compact exact records under `development` and references under `references`.
- `s04_train.py` fits ten cost predictors for each graph. Profiles 72 and 73 supply training labels. Profile 74 selects the final policy. The code fixes all choices before the reserved test.
- `s05_test.py` compares four routes on profiles 75 and 76. It also applies the selected route with the target coefficients withheld.
- `s06_analyze.py` checks all test records and makes the complete-time plot and summary.
- `s07_reduce.py` is the public entry point. Its input JSON contains `case` and `basis`. The case uses the fields in `protocol.json`. The output must be under this study's `model_test` folder.
- `s08_public_checks.py` starts a fresh public application for each graph and checks the result independently.
- `s09_pipeline.py` selects the development winners, trains the candidates, freezes validation choices, tests them, and checks the public entry point. It does not use reserved timings to select a model.
- `s10_write_report.py` writes the measured results into the paper and notes. It uses `basis_completion_appendix.tex` for the definitions and exact derivation.
- `s11_validate.py` checks records, parameter separation, source files, exact results, and storage. It also writes the guides in data folders.
- `s12_finish.py` runs the evidence checks, updates both documents and folder guides, renders both PDFs, and runs the paper checks.

Submit the development job with `qsub -o ML_model_workflow_selection/basis_completion/logs/probe.log ML_model_workflow_selection/basis_completion/s02_job.sh s03_probe.py`.

When development is complete, submit `s09_pipeline.py` with the same scheduler script. The pipeline keeps each development winner that saves at least ten percent and also keeps the preceding route. The training labels include all retries. Validation enables a predictor only when it saves at least five percent against the faster control. Unknown structures and target features outside the training range use the preceding route.

Run `s11_validate.py` after the pipeline completes. Run `s10_write_report.py` to update the document sources. Build both documents with `make -C report`. Run `report/s01_check_paper.py` to check references, figures, results, and preserved notes.

For an application, submit `s07_reduce.py --input CASE_AND_BASIS.json --output ML_model_workflow_selection/basis_completion/model_test/RESULT.json.gz` through `s02_job.sh`. Supply the required masters without target coefficients. The selected strategy can change seed limits, complete a temporary basis, or call the preceding route. Kira performs the exact algebra. All final coefficients must use the required masters.

The `protocol.json` file defines the split and candidates. The `candidate_selection.json` file records the development choice. The `resource_plan.json` file gives the storage budget. The `evidence_validation.json` file records the final checks. Generated records and fitted models stay on Hoffman and GitHub. The local report contains only compact result summaries.

The reference coefficients are used for final checks. The strategy receives only target indices, family data, and the required master basis. The current scope is seven known graph structures with rational external parameters and a symbolic dimension. This study does not claim a gain for every integral.
