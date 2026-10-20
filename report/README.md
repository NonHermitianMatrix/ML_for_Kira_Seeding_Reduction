# Optimizing Methods for Feynman Integral Reduction with Kira

The paper reports the full study. Its title page has no author or date. Read `report.pdf` for the methods, final formulas, physical uses, measured gains, and limitations. The tables compare exact methods, learned choices, all completed native physical classes, and the one-loop tensor mass classes. `notes.pdf` keeps the historical experiments and remains unchanged in this editorial update.

- `paper_integral_results.tex` connects integral structures, QCD/QFT uses, formulas, and timings.
- `s06_method_tables.py` reads saved summaries and writes `paper_native_type_rows.tex`, `paper_tensor_type_rows.tex`, and `method_table_data.json`. It does not run a scientific calculation.
- `s07_check_method_tables.py` checks this revision after the existing three paper checks.
- `writing_review.md` records the use of the user-supplied UVU scientific-writing guide and the claim checks.

The main paper now explains the whole project. It covers the constructed integral data, the first seed and row models, their native Kira tests, equation selection, models trained on complete cost, exact recurrences, shared requests, and analytic extensions. Direct original-to-optimized comparisons appear in the main results. The final 93-request update is in a supporting appendix. Each gain has its own control and scope.

# Feynman integral reduction with Kira

Read `report.pdf` for the whole-project paper. Read `notes.pdf` for the full study history.
The paper starts with the physics problem and a worked integration-by-parts example.
It then explains exact identities, learned choices, physical scope, tests, results, and limits.

The final test uses 93 requests. Median collection time changes from 45.091 to 41.137 seconds.
This is 8.8% less time than the preceding application. It is not a comparison with stock Kira.
The paper reports slower groups and unsuccessful model trials as well as gains.
The exact external coefficient audit is outside the application timers.

## Read the sources

- `report.tex` controls the paper.
- `paper_abstract.tex` and `paper_conclusion.tex` state the purpose and measured outcome.
- `paper_background.tex` defines the physics terms, integrals, seeds, and row operations.
- `paper_methods.tex` explains the exact formulas and learned decisions.
- `paper_study_design.tex` defines the physical scope, controls, and timers.
- `paper_project_results.tex` reports the main project comparisons. The older `paper_results.tex` is retained as an editorial source.
- `paper_discussion.tex` states what the results support and what remains unverified.
- `focused_derivations.tex` derives the IBP operations, learning objective, and timing measures.
- The tensor, lightlike, tree, vacuum, reconstruction, and triangle appendices give the detailed mathematics and inputs.
- `paper_references.bib` contains the external references. The paper does not cite this repository.
- `notes.tex` keeps the earlier experiments. `notes_paper_reading_guide.tex` relates them to the whole-project paper.

The current application remains `ML_model_adaptive_reduction/triangle_reduction/s32_deploy.py`.
Use `s33_batch.py` in that folder to process a request list in one call.
Read [the application guide](../ML_model_adaptive_reduction/triangle_reduction/README.md) for commands and input conditions.
This report revision changes no trained model, reduction code, or scientific measurement.

## Reproduce the figures and PDFs

Run `python s02_rewrite_figures.py` from this folder with Matplotlib available.
The script reads the saved result summaries. It performs no training or reduction.
On Hoffman, it reads the original cost-validation summary and saves compact report evidence.
Other copies can use `rewrite_cost_evidence.json` to make the same plots.
The three appendix `rewrite_*.pdf` figures show complete time, physical scope, and model-only controls.
`rewrite_figure_data.json` records their values and source hashes.

Run `make` in this folder to render both PDFs with Tectonic.
The build uses a 1.5 GiB address-space limit. The checks require each PDF to stay below 32 MiB.
Run `python s01_check_paper.py` to check references, citations, saved numerical evidence, and preserved notes.
Run `python s03_check_rewrite.py` for the new paper's figure, timing, and equation checks.
Read `rewrite_validation.json` for the result and `writing_review.md` for the evidence map.
The historical `*_validation.json` files refer to their original experiment and document versions.
Use `project_validation.json`, `rewrite_validation.json`, and `method_table_validation.json` for the present PDFs.

Keep this complete folder on Hoffman, GitHub, and the local machine.
Keep integral data, trained weights, and native reduction outputs on Hoffman and GitHub only.
Do not run an old experiment's report writer over the revised paper.
Earlier source sections and figures remain available for the notes and evidence checks.

## Whole-project paper files

- `paper_project_data.tex` explains target construction and the first models.
- `paper_project_results.tex` compares the main project outcomes and their controls.
- `paper_project_appendix.tex` derives the target construction, vacuum recurrence, and earlier estimators.
- `paper_project_structural.tex` defines the shared model and its native inputs.
- `paper_latest_appendix.tex` keeps the final 93-request protocol and results.
- `s04_project_figures.py` reads saved report evidence and creates four project-wide figures. It does not train models or run Kira.
- `s05_check_project.py` checks these results against the saved evidence. Run it after the existing paper and rewrite checks.

To refresh figures on Hoffman, use `.tools/seed-model/venv/bin/python report/s04_project_figures.py`. Then build both PDFs with the report Makefile and run `s01_check_paper.py`, `s03_check_rewrite.py`, and `s05_check_project.py`. Use a bounded single-core scheduler job for rendering. Keep older development writers separate; they can replace the manuscript.
