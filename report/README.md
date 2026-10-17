# Paper and notes

<!-- BEGIN PARAMETRIC UPDATE -->

`parametric_results.tex` contains the latest complete-time comparison.
`parametric_appendix.tex` derives the exact changes. `parametric_data.json` supplies its checked numbers.
The paper and notes include the new comparison and preserve the earlier results.

<!-- END PARAMETRIC UPDATE -->


`report.tex` and `report.pdf` contain the research paper.
`notes.tex` and `notes.pdf` contain the detailed notes and earlier experiments.
Both documents include the new complete-cost study.
The paper cites external sources and derives the model equations in its appendices.
It does not cite this repository.

## Language and structure

The paper now groups the three local models before the models that select a complete calculation.
Each section explains its question, method, result, and limits.
The comparison text names the baseline and explains the reported time measure.
The appendices keep the equations and add clearer explanations around them.
Shared section files also update the current additions in the notes.

The revision used [Mensh and Kording's guide](https://doi.org/10.1371/journal.pcbi.1005619) for paper structure.
It also examined the [Kira paper](https://arxiv.org/abs/1705.05610),
[Kira 3](https://arxiv.org/html/2505.20197v1), and
[the seed-optimization study](https://arxiv.org/abs/2502.09544) as examples of physics papers.
The revision uses original wording.
These writing references explain the editorial approach; the paper bibliography supports its scientific claims.

`editorial_revision.json` records the preserved equations, table values, figure paths, citations, and source checks.
The October 14 editorial revision changed no model, dataset, or measured result. The October 15 verification adds the measurements described below.
Keep the edited section files as the current prose sources.
Older experiment scripts can regenerate result text and replace these edits.
Review their output before replacing an edited section.

## Build and check

Run `make` in this folder to build both PDFs.
Run `make report.pdf` or `make notes.pdf` to build one document.
The `Makefile` uses the existing Tectonic installation with memory, output and time limits.
The saved figures permit a build without the integral datasets.

Run `python s01_check_paper.py` after the build.
This script checks citations, cross-references, figures, measured ratios and PDF files.
It checks the retained historical files and reconstructs the original notes from the recorded changes.
`paper_validation.json` contains the check results.
A file hash checks file identity; it does not prove a reduction.

Run `s00_make_paper_figures.py` on Hoffman to rebuild the five original paper figures.
Use `../.tools/seed-model/venv/bin/python` with the Python module loaded.
The script reads saved results and does not repeat a reduction or train a model.
`paper_figure_data.json` records its values and source files.

## Scientific sections

`paper_appendices.tex` gives the original integral definitions, model derivations and checks.
`scattering_results.tex` gives the additional scattering training study.
`workflow_results.tex` gives the complete-cost selector, full reduction tests and joint-request results.
`workflow_appendix.tex` derives the cost models and specifies parameter points and target lists.
`paper_references.bib` contains the paper's bibliography.
The remaining section files and `references.bib` support the detailed notes.

`scattering_figure_data.json`, `workflow_figure_data.json` and `batching_figure_data.json`
contain compact values for the added tables and figures.
`workflow_validation.json` records the complete experiment and application checks.
The full scientific records and model weights remain on Hoffman and GitHub.
The report specifies the integral families and target-generation rules.
It does not print all 2,301,272 original target records.

The original notes remain in Git history.
`notes_preservation.json` identifies their source and supporting files.
`notes_revision.json` records the requested changes in terminology.
`notes_README.md` explains the document names and preservation checks.
Current additions have explicit boundaries that permit reconstruction of the earlier source.

## Figure sources

The [scattering analysis](../ML_model_equation_selection/scattering_training/s02_analyze.py)
creates the two scattering figures.
The [complete-cost analysis](../ML_model_workflow_selection/s07_analyze.py)
creates the full reduction comparison.
The [joint-request plotter](../ML_model_workflow_selection/s12_plot_batching.py)
creates the batching comparison.
The [paper figure guide](paper_figures/README.md) explains each plot.
The [earlier figure guide](figures/README.md) describes the figures in the notes.

Keep the sources, bibliography, figures and both PDFs on Hoffman, GitHub and the local machine.

## Policies for each graph

The `type_specialist_results.tex` section reports the graph-specific cost study.
The `type_specialist_appendix.tex` appendix gives its physics inputs, model fits, and selection rule.
The `type_specialist_references.bib` file supplies the added external source for the notes.
The paper uses the same source in `paper_references.bib`.
The `type_specialist_figure_data.json` file contains the compact result summary.
The `type_specialist_validation.json` file records exact checks, split checks, and storage checks.
The `s01_check_paper.py` script checks these data against the report and preserved notes.
See [the study guide](../ML_model_workflow_selection/type_specialists/README.md) for source code, fitting, tests, and limits.

## Selective seed expansion

`basis_completion_results.tex` gives the new methods and measured results. `basis_completion_appendix.tex` defines the inputs, candidates, exact basis conversion, model selection, and comparison. `basis_completion_figure_data.json` contains the compact plot and table values. `basis_completion_validation.json` records the completed evidence checks. The [study guide](../ML_model_workflow_selection/basis_completion/README.md) explains all code and data. `s01_check_paper.py` also checks the new summaries against their scientific sources on Hoffman.

## Ordering comparison

`ordering_policy_results.tex` gives the new methods and measured results. `ordering_policy_appendix.tex` defines the inputs, candidates, relabelling invariance, model selection, and comparison. `ordering_policy_figure_data.json` contains the compact plot and table values. `ordering_policy_validation.json` records the completed evidence checks. The [study guide](../ML_model_workflow_selection/ordering_policy/README.md) explains all code and data. `s01_check_paper.py` also checks the new summaries against their scientific sources on Hoffman.

## Worker-count comparison

`thread_policy_results.tex` gives the new methods and measured results. `thread_policy_appendix.tex` defines the inputs, candidates, worker-count invariance, model selection, and comparison. `thread_policy_figure_data.json` contains the compact plot and table values. `thread_policy_validation.json` records the completed evidence checks. The [study guide](../ML_model_workflow_selection/thread_policy/README.md) explains all code and data. `s01_check_paper.py` also checks the new summaries against their scientific sources on Hoffman.

<!-- BEGIN ADAPTIVE REDUCTION -->

## Adaptive policy and exact preprocessing

`adaptive_results.tex` reports the new model and its complete-cost tests.
`adaptive_appendix.tex` defines its inputs, training objective, and recovery rule.
It also derives the exact zero-sector projection.
`adaptive_reduction_data.json` contains the checked compact results.
`higher_scattering_results.tex` records the earlier component controls and bounded scattering attempts.
Both the paper and notes include these additions.
The archived notes can still be reconstructed exactly by removing their marked current-update blocks.
Run the new study's `s06_analyze.py` and `s07_report.py` before rebuilding both PDFs.
Then run `report/s01_check_paper.py`.
The current study changes the implementation, model, measurements, and report.
The earlier editorial audit remains a historical record.

<!-- END ADAPTIVE REDUCTION -->

<!-- BEGIN HIGHER SCATTERING VERIFICATION -->

## Component effects and higher-loop scattering

`higher_scattering_results.tex` compares the methods on common targets and records the new scattering tests.
`higher_scattering_appendix.tex` defines the families and derives the initialization-domain restriction.
`higher_scattering_data.json` contains compact measured values.
`higher_scattering_validation.json` records the evidence audit.
The new section separates learned decisions, fixed strategies, shared requests, and the restricted vacuum recurrence.
It retains failed cases and gives no speedup for an unfinished calculation.
The initial editorial audit remains a record of the earlier language-only revision.
The current revision adds new scientific results.
Run the [study analysis](../Kira_comparison/higher_scattering/s07_analyze.py) before rebuilding its figure.
Run both report checks after building the PDFs.
The main paper and the current additions in the notes include the new results.

<!-- END HIGHER SCATTERING VERIFICATION -->

The workflow appendix now states sunrise masses `(3,7,13)` and vacuum masses `(1,1,1,13,13,53+2h)`.
These values match the stored workflow and specialist case definitions.
This correction changes the description only; the saved calculations and timings remain unchanged.

<!-- BEGIN PORTFOLIO REPORT -->

## Final complete-cost portfolio

`portfolio_results.tex` gives the current method and its matched results.
`portfolio_appendix.tex` derives the cost labels and prediction gate.
`portfolio_data.json` contains compact checked evidence without model weights.
`notes_native_families.tex` supplies the denominator definitions needed to read the notes independently.
The original cost-policy study remains in the paper appendix and in the notes.
Use `s11_finalize.py` to rebuild the evidence and both documents in order.

<!-- END PORTFOLIO REPORT -->

<!-- BEGIN COVERAGE STUDY -->
`coverage_results.tex` and `coverage_appendix.tex` describe the broader tests.
`coverage_data.json` supplies their measured values. The new figures show coverage and matched complete times.
<!-- END COVERAGE STUDY -->






<!-- BEGIN LEARNED SEED BOUNDS -->
`learned_bounds_results.tex` describes the new model and matched controls.
`learned_bounds_appendix.tex` defines the inputs and derives the cost formulas.
`learned_bounds_data.json` contains the compact test evidence.
`learned_bounds_validation.json` records the completed checks.
The figures show complete-time effects and generated-equation counts.
Both PDFs include these results.
<!-- END LEARNED SEED BOUNDS -->

<!-- BEGIN EQUATION REFINEMENT -->
`equation_refinement_results.tex` explains the new filter and complete-time comparison.
`equation_refinement_appendix.tex` gives the sampling weights, models, and evaluation definitions.
`equation_refinement_data.json` stores the compact result summary.
`equation_refinement_validation.json` records the final checks.
Both PDFs include the new results.
<!-- END EQUATION REFINEMENT -->



<!-- BEGIN BATCH POLICY -->
## Target batch comparison

`batch_policy_results.tex` gives the model and measured results.
`batch_policy_appendix.tex` defines the physical requests and derives the method.
`batch_policy_data.json` contains the checked timing summaries.
`batch_policy_validation.json` identifies the final checks and rendered PDFs.
The study guide explains how to reproduce the calculation.
<!-- END BATCH POLICY -->

<!-- BEGIN BANANA -->
## Exact higher-loop specialization

`massless_banana_results.tex` gives the physics and results.
`massless_banana_appendix.tex` derives the formula and defines each comparison.
`massless_banana_data.json` and `massless_banana_followup_data.json` contain timing and check summaries.
`integral_route_data.json` gives the combined-interface application results.
The source and full records are in `ML_model_adaptive_reduction/massless_banana/`.
<!-- END BANANA -->


<!-- BEGIN COST-TRAINED SEED RESULTS -->
`seed_geometry_results.tex` gives the new seed-policy measurements.
`seed_geometry_appendix.tex` defines the model and derives its distance and counting formulas.
`seed_geometry_data.json` contains the compact timing evidence.
The first evolved boundary and the broader cost-selection study have separate controls.
Both documents include these results.
See `../ML_model_seed_selection/cost_geometry/README.md` for the code and full records.
<!-- END COST-TRAINED SEED RESULTS -->


<!-- BEGIN JOINT CONFIGURATION -->
`joint_policy_results.tex` gives the latest model and exact scale-reuse comparisons.
`joint_policy_appendix.tex` defines the cases and derives the scale identity.
`joint_policy_data.json` contains the compact measured evidence.
`joint_policy_validation.json` records the final checks.
Read `../ML_model_seed_selection/joint_policy/README.md` for the full data and commands.
<!-- END JOINT CONFIGURATION -->
