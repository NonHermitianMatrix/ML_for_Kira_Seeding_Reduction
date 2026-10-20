<!-- DIRECT ANALYTIC CURRENT BEGIN -->
# Current integral decomposition method

Use `ML_model_adaptive_reduction/direct_analytic/s23_deploy.py`.
Read the [current application guide](../ML_model_adaptive_reduction/direct_analytic/README.md) for commands, exact domains, models, and limits.
The method combines analytic formulas with measured-cost native choices.
The paper reports the current comparison. The notes retain the earlier experiments.
Both documents include analytic derivations, exact checks, failures, and limits through 13 loops.
This does not establish coverage of every high-loop scattering family.

The sections below describe earlier versions.
<!-- DIRECT ANALYTIC CURRENT END -->

## Earlier exact vacuum and learned application

<!-- LIGHTLIKE STUDY BEGIN -->
The preceding application is `ML_model_adaptive_reduction/lightlike_reduction/s05_runtime.py`.
Read the [exact and learned reduction guide](../ML_model_adaptive_reduction/lightlike_reduction/README.md).
The paper now focuses on exact identities, learned Kira decisions, and complete time.
The notes retain the earlier experiments. Both PDFs include the new measured comparison.
`paper_before_lightlike.tex` preserves the preceding main-paper narrative in the report folder.
The historical numerical audits remain active; old labels are checked in retained sources.
Earlier-paper references and citations are checked in the current paper itself.
<!-- LIGHTLIKE STUDY END -->

Read [the current method guide](../ML_model_adaptive_reduction/vacuum_learning/README.md).
Use vacuum_learning/s03_runtime.py with --method integrated.
This version adds exact single-mass vacuum trees and a newly trained native seed-choice model.
The paper and notes give separate exact and ML measurements, failures, and domain limits.

## Preceding two-point and learned application

Read [the current method guide](../ML_model_adaptive_reduction/propagator_trees/README.md).
Use propagator_trees/s02_runtime.py with --method integrated.
The method reduces supported connected two-point trees exactly, then retains the preceding exact formulas and trained Kira choices for other inputs.
The paper and notes state the domain, native index limit, complete times, and separate ML comparison.

## Preceding exact-cancellation application

Read [the current method guide](../ML_model_adaptive_reduction/gamma_cancellation/README.md).
Use gamma_cancellation/s02_runtime.py with --method integrated.
The method cancels complete Gamma factors before finite expansion and shares subtree calculations within target batches.
It preserves the preceding native models and exact methods for other supported inputs.
The paper and notes give the derivation, complete-time comparisons, and limits.

## Preceding connected bubble-tree application

Read [the current method guide](../ML_model_adaptive_reduction/loop_coverage13/README.md).
Use loop_coverage13/s02_runtime.py with --method integrated.
The new exact identity reduces connected massless bubble trees through thirteen loops.
The application keeps the preceding trained choices for other supported inputs.
The paper and notes give the derivation, fresh comparisons, coverage, and limits.
Earlier methods retain their original data and claims.

## Preceding analytic batch report files

analytic_batch_method.tex explains exact triangle reduction and learned target grouping.
analytic_batch_results.tex gives model admission, reserved times, controls, and failures.
analytic_batch_appendix.tex derives the coefficient and defines all training and test inputs.
analytic_batch_data.json contains the compact measured summary.
analytic_batch_validation.json identifies the current evidence and PDF checks.
paper_figures/analytic_batch.pdf compares complete time and the separate batch-model effect.
The notes_analytic_batch files give the same current evidence in the detailed notes.
Use s15_finish.py in analytic_batch to rebuild the current sections and check both PDFs.
Earlier study writers can replace current prose. Use the current writer for this extension.

## Earlier fast exact and learned decomposition

Use [the preceding method guide](../ML_model_adaptive_reduction/fast_decomposition/README.md) for exact formulas, retained seed selection, tests, and limits.
The final entry point is s12_deploy.py in fast_decomposition. Use --method final.
Complete-time validation keeps the fixed recurrence strategy and the retained seed model.
The trained recurrence tree remains available for comparison.
The paper and notes include the initial 65-request timing test and the 110-request coverage audit.
They also include full-cost validation and the separate twelve-request test of the final application.
Earlier studies retain their original evidence.

## Preceding exact-recurrence study

The preceding application added an exact scalar one-loop recurrence to the frozen learned Kira workflow.
That version used the recurrence for direct rational kinematics and kept native Kira or earlier exact formulas for symbolic inputs.
Read [the method guide](../ML_model_adaptive_reduction/analytic_decomposition/README.md) for the code, tests, and supported inputs.
The paper studies loop-integral decomposition into master integrals. The notes retain earlier methods and results.

<!-- BEGIN COMPLETE TIME SELECTION -->
The earlier hybrid application is ML_model_adaptive_reduction/hybrid_experts/s01_runtime.py.
Read its README for exact routes, the sparse expert, complete-time controls, and measured limits.
The preceding broad comparison remains in refined_time_policy/.
The paper and notes retain those comparisons.
<!-- END COMPLETE TIME SELECTION -->

# Paper and notes

`report.tex` and `report.pdf` contain the research paper.
`notes.tex` and `notes.pdf` contain the detailed notes and earlier experiments.
Keep both documents on Hoffman, GitHub, and the local machine.
Keep integral data and trained weights on Hoffman and GitHub only.

## Read the paper

The paper explains the physical problem, the three learned decisions, and their direct timing comparisons.
It then tests a shared cost model with whole families and higher loop orders held out.
The paper separates learned savings from fixed tuning and exact mathematical shortcuts.
All native test outcomes remain in the coverage table, including failures and unsupported inputs.

`paper_abstract.tex` and `paper_conclusion.tex` state the final measured results.
`paper_derivations.tex` derives the identities, model equations, and timing measures.
`paper_extra_kinematics.tex` defines the additional scattering inputs.
`general_policy_results.tex` reports the new shared-model test.
`general_policy_data.json` contains its compact result summary.
`paper_references.bib` contains external scientific references. The paper does not cite this repository.

## Read the notes

The notes preserve the earlier models, data construction, exact recurrences, and secondary timing studies.
`notes_supplement.tex` contains the unique historical material moved from the preceding paper.
The original paper remains in Git history.
`notes_additional_references.bib` adds the external references needed by this supplement.
The other result and appendix files support the notes and preserve their original controls and limits.

Earlier additions use explicit markers. `notes_revision.json` and `notes_preservation.json` allow the checker to reconstruct the original notes.
Do not remove historical measurements when a later model changes the deployed method.

## Build and check

Run `make` in this folder to build both PDFs with Tectonic.
Run `python s01_check_paper.py` after the build.
The checker reads actual included sections. It checks citations, references, figures, result ratios, and historical preservation.
It retains the earlier result checks and adds the shared-model coverage checks.
`paper_validation.json` records the outcome.

The Makefile limits memory, output size, and build time.
The saved figures permit a build without downloading the integral datasets.

## Generate the retained shared-model figures

Run `../ML_model_adaptive_reduction/general_policy/s05_analyze.py` on Hoffman after both model trials finish.
Use the existing scientific Python environment described in that folder's README.
The script reads saved results and does not train models or repeat Kira reductions.
It writes the shared-model time and coverage plots, and the compact retained-model plot.
`paper_figures/README.md` explains each plot's message and controls.

Older scripts can overwrite current prose with historical result text.
Use `../ML_model_adaptive_reduction/fast_decomposition/s11_validate.py` for the complete study checks on Hoffman.
That script can regenerate result prose. Preserve editorial changes before you run a writer.
For editorial changes alone, use `make` and `python s01_check_paper.py`.

Read [ARCHIVED_CODE_GUIDE.md](ARCHIVED_CODE_GUIDE.md) for earlier report generators and their evidence files.
Use the current writer for the concise paper. Older writers can replace its text.

## Complete preparation comparison

`preparation_results.tex` reports all outcomes and matched full workflow times.
`preparation_appendix.tex` derives the cost-and-failure objective and defines the test inputs.
`preparation_data.json` contains the compact comparison evidence.
`notes_general_methods.tex` places the shared model and physical definitions in the notes.
Scripts s17 through s19 in `general_policy/` produce these files and the preparation figure.
The earlier `s13_finish.py` writer runs them after the shared-model writer. Use the current extension writer for new changes.

## Thirteen-loop extension

`factorized_results.tex` gives the corrected method and measured results.
`factorized_appendix.tex` derives block factorization and the vacuum and massless numerator formulas.
`factorized_data.json` stores compact checked results.
`factorized_initial_notes.tex` preserves the initial grid and the basis correction.
`notes_factorized_appendix.tex` gives the same derivation with note references.
Run scripts s12 through s14 in `factorized_policy` to update this extension.
The older report writers can replace current prose.
Use the current writer and check both PDFs after changes.




## Complete-time method selection

refined_time_results.tex gives the earlier nine-candidate method and reserved results.
refined_time_appendix.tex derives the tighter master-basis cutoff.
total_time_appendix.tex gives the shared cost objective, features, and target definitions.
refined_time_data.json contains the compact checked measurements.
refined_time_validation.json records that study and its earlier PDF checks.
The notes preserve total_time_results.tex, its earlier comparison, and both detailed parameter records.

## Integrated expert report

hybrid_expert_results.tex gives the combined method and direct comparisons.
hybrid_baseline_summary.tex summarizes the preceding broad baseline in the main paper.
hybrid_expert_appendix.tex defines fresh targets, candidate boundaries, and deployment rules.
The notes use matching copies with references to the historical derivations.
hybrid_expert_data.json and hybrid_expert_validation.json contain that study and its earlier PDF checks.

## Earlier fast-decomposition files

fast_decomposition_method.tex explains the exact changes and trained recurrence selector.
fast_decomposition_results.tex gives the initial timing comparison and coverage audit.
fast_decomposition_appendix.tex derives the identities and defines the inputs.
fast_deployment_results.tex gives complete-time validation and the separate final test.
fast_deployment_appendix.tex defines the fresh final-test inputs.
The matching data JSON files contain the checked result summaries.
fast_decomposition_validation.json identifies the preceding publication checks.
The matching notes files preserve the same evidence in the detailed document.

## Connected-tree report files

loop_coverage13_method.tex explains the physical domain and its integration with the learned workflow.
loop_coverage13_results.tex gives all new timing and coverage results.
loop_coverage13_appendix.tex derives the bubble, triangle, and rational reduction formulas.
loop_coverage13_data.json contains the report summary.
loop_coverage13_validation.json records the current checks and PDFs.
paper_figures/loop_coverage13.pdf shows completed coverage by type and loop order.
paper_figures/loop_coverage13_time.pdf shows complete times for the connected trees.
The notes_loop_coverage13 files retain the same current evidence in the notes.
Use loop_coverage13/s12_finish.py to rebuild this extension after completed tests.
Earlier document writers can replace current prose. Use the current writer for the latest paper.

The current tensor extension appears in tensor_reduction_results.tex and tensor_reduction_appendix.tex.
The appendix derives angular moments, signed-index IBP, and arithmetic with factored dimension poles.
Matching notes files preserve the same derivation and evidence.
The compact data file is tensor_reduction_data.json.
The structured coefficient outputs and model weights stay in the cluster study folder and GitHub.
