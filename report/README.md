# Feynman integral reduction with Kira

Read `report.pdf` for the focused paper. Read `notes.pdf` for the full study history.
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
- `paper_results.tex` reports the measured comparisons.
- `paper_discussion.tex` states what the results support and what remains unverified.
- `focused_derivations.tex` derives the IBP operations, learning objective, and timing measures.
- The tensor, lightlike, tree, vacuum, reconstruction, and triangle appendices give the detailed mathematics and inputs.
- `paper_references.bib` contains the external references. The paper does not cite this repository.
- `notes.tex` keeps the earlier experiments. `notes_paper_reading_guide.tex` relates them to the focused paper.

The current application remains `ML_model_adaptive_reduction/triangle_reduction/s32_deploy.py`.
Use `s33_batch.py` in that folder to process a request list in one call.
Read [the application guide](../ML_model_adaptive_reduction/triangle_reduction/README.md) for commands and input conditions.
This report revision changes no trained model, reduction code, or scientific measurement.

## Reproduce the figures and PDFs

Run `python s02_rewrite_figures.py` from this folder with Matplotlib available.
The script reads the saved result summaries. It performs no training or reduction.
On Hoffman, it reads the original cost-validation summary and saves compact report evidence.
Other copies can use `rewrite_cost_evidence.json` to make the same plots.
The three `rewrite_*.pdf` figures show complete time, physical scope, and model-only controls.
`rewrite_figure_data.json` records their values and source hashes.

Run `make` in this folder to render both PDFs with Tectonic.
The build uses a 1.5 GiB address-space limit. The checks require each PDF to stay below 32 MiB.
Run `python s01_check_paper.py` to check references, citations, saved numerical evidence, and preserved notes.
Run `python s03_check_rewrite.py` for the new paper's figure, timing, and equation checks.
Read `rewrite_validation.json` for the result and `writing_review.md` for the evidence map.
The historical `*_validation.json` files refer to their original experiment and document versions.
Use the latest rewrite validation for the present PDFs.

Keep this complete folder on Hoffman, GitHub, and the local machine.
Keep integral data, trained weights, and native reduction outputs on Hoffman and GitHub only.
Do not run an old experiment's report writer over the revised paper.
Earlier source sections and figures remain available for the notes and evidence checks.
