<!-- BEGIN PREPARATION COST MODEL -->
`ML_model_adaptive_reduction/general_policy/preparation/` contains the attempt-time and failure model.
Its controls separate learned choices from basis reuse and smaller exact checks.
`general_policy/recovery/` records fresh tests of recovery from an incomplete stored basis.
Use `general_policy/s20_prepare_resilient.py` for that revised preparation application.
Read the folder guides for complete-time results, failures, and supported inputs.
<!-- END PREPARATION COST MODEL -->

<!-- BEGIN SHARED STRUCTURAL MODEL -->
The current shared cost model is in `ML_model_adaptive_reduction/general_policy/`.
It uses structural features and tests whole-family and higher-loop transfer.
Read its guide and coverage records for the measured domain and failures.
The concise paper is `report/report.pdf`; the detailed history is `report/notes.pdf`.
<!-- END SHARED STRUCTURAL MODEL -->

# Adaptive Kira reduction

<!-- BEGIN LEARNED SEED BOUNDS -->
Read [learned seed bounds](learned_seed_bounds/README.md) for the new cost-trained comparison.
Its native and fixed controls disable every earlier model.
Read its domain limits before use.
The earlier portfolio remains available for comparison.
<!-- END LEARNED SEED BOUNDS -->




<!-- BEGIN PARAMETRIC UPDATE -->

The previous interface is `s24_parametric_runtime.py`. Read [the revised preparation guide](parametric_preparation/README.md).
The earlier `s17_reduce.py` interface remains available as the matched baseline.

<!-- END PARAMETRIC UPDATE -->


Use [the earlier portfolio guide](selective_expansion/README.md) for that model and application.
The earlier entry point is `s17_reduce.py`.
The first study below explains the earlier cost model and exact preprocessing.

This folder contains models for a policy that selects a complete reduction calculation.
The models predict relative calculation cost from the integral family and target indices.
Their training labels include failed attempts and the time needed to recover.
Kira performs the exact algebra.

The model can select seed limits, integral ordering, or an existing equation filter.
Direct seed expansion can avoid an unsuccessful narrow attempt.
The policy replaces the sequence of earlier strategy selectors for this experiment.
Earlier models and negative results remain available in their original folders.

## Inputs and outputs

`cases.json` defines each integral family, target batch, and data split.
Rational profiles 301 and 302 supply training data. Profile 303 supplies validation data.
Profile 304 supplies test data.
A registered condition can add a fresh four-loop confirmation at profile 305.
Read `conditional_reference_protocol.json` for its trigger and seed limits.
The original failed check remains in the results.
The symbolic cases use different target indices in each split.
The graph structures appear in training and testing.
These tests do not measure transfer to unseen graphs.

`training/` and `validation/` contain complete timing and coefficient records.
`trained_model/candidates.json` stores nine fitted candidate models.
`trained_model/freeze.json` stores the selected model and its fixed control.
`model_test/` contains three timed repetitions per method and applications without supplied answers.
`references/` contains expanded native reductions and separate enlarged checks for test cases.
`application_test/` checks the public entry point.
`integration_test/` separates the two exact preprocessing changes from learned choices.
`summary.json` contains the checked aggregate results.

The seven choices are `native`, `tight`, `dots`, `rank`, `order5`, `equation`, and `expanded`.
The first four change the seed region. `order5` changes Kira's integral ordering.
`equation` uses a previously trained equation tree before coefficient construction.
The new policy learns which choice has the lowest complete cost.
It compares regression trees, random forests, and extremely randomized trees.
The ensembles contain 48 trees. Validation selects the depth and decision gate.
The production evaluator uses the stored tree splits and has no training-library dependency.

Every calculation receives a prescribed master basis.
If its first choice is insufficient, it retries with native choices and then expanded seeds.
The complete time includes all retries, input preparation, prediction, exact comparison, and cleanup.
Offline references, imports, and initial model loading are outside repeated timing.
The application entry point also records model-loading and choice time when it loads the model itself.
The method does not establish that the supplied master basis is minimal.

## Execution order

Use the existing Hoffman environment at the project root.
Run scientific calculations through the scheduler. After preparation, the graph-control and preprocessing comparisons can run as two independent jobs.
First-study jobs reserve one core and 8 GB of memory.
The final portfolio uses two cores with 8 GB total memory.
Read the current application section for its execution order.

1. Run `s00_build.py` to build a separate native executable and generate `s01_native_runner.py`.
2. Submit `s04_job.sh s03_pilot.py` with one slot to check the preprocessing changes.
3. Submit `s04_job.sh s05_study.py` after the pilot succeeds.
4. Submit `s04_job.sh s09_integration_check.py` after the study finishes.
5. Run `s06_analyze.py` to audit results and generate the comparison plot.
6. Run `s07_report.py` to update the paper and notes.
7. Run `s10_document.py` to update the folder guides.
8. Build both PDFs with the report Makefile and run the report checks.

`s02_runtime.py` supplies one bounded reduction interface and exact coefficient checks.
`s05_study.py` creates cases, measures candidate costs, trains models, selects on validation data, and tests frozen weights.
`s08_reduce.py` is the application entry point. It needs a case file, a master-basis file, and an output path.
The basis file contains a JSON list of integral index vectors.
The case format matches a record in `cases.json`.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/s08_reduce.py \
  --case case.json --basis basis.json --output result.json.gz
```

Run this command in a scheduled job with node scratch available.
The output includes coefficients, the selected action, recovery attempts, and complete times.
Unknown graph labels use native choices.
Supported predictions cover the tested graph structures and target ranges only.

## Exact preprocessing

The executable is `.tools/kira-adaptive/kira`.
The earlier executable and source remain unchanged.
`KIRA_INDEX_SECTOR_FILES=1` indexes existing sector files before triangular reduction and back-substitution.
`KIRA_PROJECT_ZERO_CRITERION=1` removes unused parameter terms from the zero-sector criterion.
The second option requires `KIRA_RESTRICT_SECTOR_INIT=1` and the documented sector-domain conditions.
Unset each variable to disable that option.
The sector-wise triangular mode remains unchanged.

`integration/` contains the source patches and build commands.
The zero-sector projection preserves the full polynomials used by other operations.
The report derives the polynomial identity that permits this projection.
These exact changes are separate from the learned policy.
The Kira source uses the upstream GPL license. See the existing build instructions and upstream license.

`development_initial/` and `development_index_only/` retain earlier partial implementations and their measurements.
The interrupted four-loop development attempt supplies no completed timing result.
`development/` contains the final exact parity checks against earlier independent references.

## Resources

Each first-study job reserves one slot with 8 GB of memory.
The two independent comparison jobs reserve at most 16 GB together.
Each Kira attempt uses one worker. Initial pilots reserved two slots with 4 GB per slot.
The total memory reservation remains 8 GB.
The driver limits solver address space to 6,144 MiB and process-tree resident memory to 5,200 MiB.
Each attempt uses at most 32 MiB of temporary files.
The two comparison jobs use at most 64 MiB together.
This folder has a 64 MiB retained-data limit.
The combined project ceiling remains 10,000,000,000 bytes.
Generated data and models stay on Hoffman and GitHub. Only report artifacts are copied locally.

The analysis reports all completed checks and all failed references.
Three timing repetitions give descriptive comparisons. They do not establish universal or globally optimal speedups.

<!-- BEGIN ADAPTIVE REDUCTION BUILD -->

## Build requirements and final checks

Use the source and dependency versions from the existing Kira build in `.tools/kira-build/`.
The builder reads its compiler commands from `compile_commands.json`.
It also reads the restricted-sector source and link command from `Kira_comparison/higher_scattering/`.
That build uses the earlier equation-filter and temporary-data changes.
The parent folder guides give their build order and dependency setup.
Run `s00_build.py` only after these parent builds exist.
`integration/build.json` records the exact compiler and linker inputs used in this study.
The new executable has a separate path, so earlier results retain their original binaries.

Training requires NumPy and scikit-learn in the existing seed-model environment.
Exact checks require SymPy. Figure generation requires Matplotlib.
The application evaluates the saved tree arrays directly.
It still uses the common Python reduction driver and its dependencies.

`s11_finalize.py` runs both study audits, writes both documents, updates the guides, and builds both PDFs.
It then runs `report/s01_check_paper.py` and writes `validation.json`.
This script does not publish files or change model weights.
`study_final.log`, `prepare.log`, `graph.log`, `integration.log`, and `finalize.log` record the scheduled stages.
`job_plan.json` records their dependencies and resource allocations.
For `s09_integration_check.py`, `ADAPTIVE_CHECK_STAGE=prepare` freezes predictors and completes any conditional reference.
It writes `prepared_checks.json` before the independent comparisons can start.
`ADAPTIVE_CHECK_STAGE=graph` runs the graph-specific controls.
`ADAPTIVE_CHECK_STAGE=integration` runs the public applications and exact-preprocessing comparison.
These two stages write separate folders and can run in parallel after preparation succeeds.
Run final checks only after both stages succeed.
Without this variable, `s09_integration_check.py` runs all three stages in sequence.
Interrupted development logs remain separate from completed measurements.
`resource_plan.json` records memory and storage allowances.
`conditional_reference_protocol.json` records the conditional four-loop check before model fitting.
`followup_cases.json` exists only when that condition is used.
`s12_graph_policy.py` selects a fixed setting for each graph from validation data.
It also fits three local regression trees for each graph with at least four training cases.
The local tree depths are one, two, and three. Each leaf needs at least two training cases.
The local trees add the largest individual propagator power and the mean number of dotted propagators to the 18 global inputs.
Validation compares the local trees with the global model and selects a prediction gate.
It permits predictions only when they save at least two percent in validation and win both repetitions.
`graph_control_protocol.json` records this rule before any reserved timing comparison.
`trained_model/graph_candidates.json` stores the local fitted trees and their training case identifiers.
`trained_model/graph_gate.json` stores the selected settings and guard decisions.
The public application uses this guard when it is present.
Repeated calls keep the model objects in memory and reload them when their files change.
Source and executable checks reuse their results while the file identity, size, and modification time remain unchanged.
Each reduction still starts a fresh Kira process and recomputes its coefficients.
`s09_integration_check.py` runs its matched comparisons before the application and preparation checks.
No failed or unfinished reference receives a speedup estimate.

<!-- END ADAPTIVE REDUCTION BUILD -->

<!-- BEGIN ADAPTIVE REDUCTION -->

## Checked results

The selected model is `tree_8` with 1 tree(s).
It uses 47 training cases and 26 validation cases.
The reserved test completes 26 batches and 234 timed workflows.
All completed outputs pass exact coefficient comparisons.
The sums of batch median times are 111.268782 seconds for native choices, 111.304633 seconds for the fixed control, and 110.693321 seconds for the learned policy.
The learned/native ratio is 0.994828.
The learned/fixed ratio is 0.994508.
The public interface passes 9 additional batch checks.
The stronger graph-specific comparison contains 234 exact reductions.
Its validated-policy/fixed ratio is 0.981816.
The validated policy enables predictions in 3 graph structures.
Read the summary for individual graphs, unsuccessful references, and exact preprocessing comparisons.

<!-- END ADAPTIVE REDUCTION -->

<!-- BEGIN CURRENT PORTFOLIO -->

## Current portfolio application

The current application is `ML_model_adaptive_reduction/s17_reduce.py`.
It selects a complete strategy from validation-supported models and fixed settings.
Read [selective_expansion/README.md](selective_expansion/README.md) for the final comparison with the previous workflow.
Use a scheduled two-core allocation with 8 GB total memory.
Pass one family-and-target JSON file and a JSON list of master index vectors.
The case format follows `selective_expansion/protocol.json`.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/s17_reduce.py --case case.json --basis basis.json --output ML_model_adaptive_reduction/selective_expansion/application_test/result.json.gz
```

For repeated calls, create `s17_reduce.Reducer()` once, call `reduce(case, basis)`, then call `close()`.
Keep the supplied basis explicit. Completion does not prove that this basis is minimal.
The interface accepts integer index vectors with at most 31 entries and no cut propagators.
All targets and masters must belong to the declared top sectors or their subsectors.
An empty master list is valid for a batch that reduces to zero.
Initial loading is reported separately. Every reduction recomputes its coefficients.
The previous-workflow service loads only when a selected strategy needs it.
Its first-use loading cost is part of that reduction's application time.
Later calls keep this service loaded until `close()`.
The optional `eager_previous=True` constructor is a timing control.
Read `selective_expansion/application_loading/` for six matched single-request checks.
The earlier immediate-loading source and checks remain in `selective_expansion/application_eager/`.
Unknown graph structures or feature ranges use native settings.
The current portfolio tests contain one to three targets per batch.
Earlier larger-batch and restricted-vacuum methods retain their separate guides and results.
Failures after all bounded attempts return an unsuccessful result.

<!-- END CURRENT PORTFOLIO -->

<!-- BEGIN DOCUMENT CHECKS -->

## Document checks during training

`s20_check_initial_report.py` audits and builds the completed first study while the portfolio run continues.
It changes no training data, fitted models, or reserved choices.
`initial_document.log` preserves the first notes build, which stopped at a missing notation command.
`initial_document_fixed.log` records the repaired build and the successful document checks.
`s11_finalize.py` adds the completed portfolio results, builds both final PDFs, and checks the full result.
`s21_check_application.py` can run the public checks as a separate two-core job after the model is frozen.
It checks exact results, an unsupported graph, invalid input types, cut-propagator rejection, and a scaleless zero integral.
It also checks deferred service loading and measures six complete application requests.
Read `job_plan.json` for the scheduled stage dependencies.

<!-- END DOCUMENT CHECKS -->

<!-- BEGIN BOUNDED CONTROL -->

## Bounded preprocessing control

The four-loop control without the two new exact changes exhausted both bounded attempts.
The original record and log remain unchanged.
`s19_finish_controls.py` completes the other pre-specified settings.
It omits further repetitions of a control after its bounded failure.
`integration_continuation.json` records this continuation and its trigger.
`integration_completion.json` lists failed controls and omitted repetitions.
Failed controls receive no completion-time median or speedup factor.
The three-loop matched comparison and the four-loop indexing-to-projection comparison retain their completed repetitions.

<!-- END BOUNDED CONTROL -->



<!-- BEGIN EQUATION REFINEMENT -->
The [equation refinement study](../ML_model_equation_selection/bound_refinement/README.md) keeps tuned seed settings and trains an earlier equation filter.
Its comparison measures the added ML effect after seed tuning.
<!-- END EQUATION REFINEMENT -->



<!-- BEGIN BATCH POLICY -->
## Target batch selection

Read [batch_policy/README.md](batch_policy/README.md) for the learned division of target batches.
The study compares the previous workflow and separately tuned controls.
It retains exact checks and failed requests.
<!-- END BATCH POLICY -->

<!-- BEGIN BANANA -->
## Analytic and learned routing

The [massless banana guide](massless_banana/README.md) describes the combined interface.
A physical-domain check selects a proved formula for one scalar two-point family.
Other supported requests use the frozen native batch workflow.
Analytic savings and ML savings remain separate.
<!-- END BANANA -->

portfolio_policy/ adds family-aware seed-cost models, exact sector-storage checks, and full-coordinate scalar checks. Read its README for the tested scope.
