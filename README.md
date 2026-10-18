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

# Project guide

<!-- BEGIN ADAPTIVE REDUCTION -->
## Current reduction interface

Use [the family-aware application](ML_model_adaptive_reduction/portfolio_policy/README.md) for individual target batches.
It retains exact scalar formulae and uses validation-selected learned or fixed seed choices.
Other inputs retain the preceding sparse-seed, equation-filter, and native paths.
Use [the joint-configuration application](ML_model_seed_selection/joint_policy/README.md) for its supported scale-reuse sequences.
The new folder also contains a separate exact sector-storage executable and its checks.
Kira keeps native row choices and exact algebra.
Read each guide for the measured physical domain and timing controls.
Earlier studies remain available. Their speedup factors cannot be multiplied.
<!-- END ADAPTIVE REDUCTION -->

This project studies machine learning for exact Feynman integral reduction with Kira.
A seed is an integral index vector that supplies integration-by-parts identities.
A master integral is a retained basis integral.
A target is an integral or an expression that must be reduced.

The earlier single-batch comparison uses [worker-count selection](ML_model_workflow_selection/thread_policy/README.md).
It retains the preceding learned seed strategy and chooses the Kira worker count once per batch.
The measured scope is seven known graphs at one through three loops, with new rational parameter values.
Summed median time changes from 82.21 to 78.73 seconds in the reserved comparison.
The retained frozen policy uses at most two Kira workers. Use the two-core application wrapper.
The earlier one-core comparison uses [selective seed expansion](ML_model_workflow_selection/basis_completion/README.md).

Read [the paper](report/report.pdf) for the methods, derivations, results and limits.
Read [the notes](report/notes.pdf) for the earlier experiments.
The seed model and equation model have separate tested uses.
The retained method uses Kira's native row choices.
The large vacuum speedup also uses exact recurrences and repeated coefficients.
It is not a measured gain from machine learning alone.

For compatible target requests, use [the joint application](ML_model_workflow_selection/README.md).
Its standard route keeps the best fixed training strategy and makes learned choices optional.
The paired-request comparison gives 48.3 percent less time across seven graph structures at one through three loops.
The gain comes mainly from sharing the reduction.

Start with [the integral collection](integrals/README.md).
Then read the model folder for the required task.
Use [early equation selection](ML_model_equation_selection/early_generation/README.md) for the supported native reductions.
Use [the symbolic application](Kira_comparison/generalization/README.md) for the tested new scattering families.

A README describes the files directly inside its folder.
Child folders have their own READMEs.
Script numbers show the recorded development order.
They do not require every historical script to run again.
Archived code and earlier failed experiments remain available for comparison.

The primary project copy is on Hoffman.
Integral data and model data stay on Hoffman and GitHub.
The report and notes also have local copies.
Keep combined project storage below 10,000,000,000 bytes.
Run training and reductions in scheduled jobs.
Keep the limits in each job script and resource plan.

The guides use ASD-STE100 sentence rules and consistent technical terms.
See the [ASD specification](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).
Exact file names, commands, symbols and option values remain unchanged.
JSON files contain named data fields.
JSONL files contain one record per line.
The suffixes `.gz` and `.xz` identify compressed files.
The project readers restore these records without changing the stored files.
NPZ files contain named NumPy arrays.
PT files contain saved PyTorch model data.
A checkpoint contains saved model parameters and, where present, the optimizer state.
A fallback repeats an incomplete selected reduction with native equations.
A SHA-256 value identifies file content for a file check.
A matching file check does not prove a physical or mathematical claim.

## Data and supporting files

- [.gitattributes](.gitattributes): This file supports the calculation described in the parent guide.

- [.gitignore](.gitignore): This file supports the calculation described in the parent guide.

- [rules.md](rules.md): This document gives additional instructions or earlier notes.

## Child folders

- [Kira_comparison](Kira_comparison/README.md).

- [ML_model_equation_selection](ML_model_equation_selection/README.md).

- [ML_model_reduction](ML_model_reduction/README.md).

- [ML_model_seed_selection](ML_model_seed_selection/README.md).

- [ML_model_workflow_selection](ML_model_workflow_selection/README.md).

- [documentation](documentation/README.md).

- [integrals](integrals/README.md).

- [report](report/README.md).

## Additional scattering training

Read [the new scattering study](ML_model_equation_selection/scattering_training/README.md) for training on the three previously unsupported structures.
It contains new seed and equation trees, separate validation and test batches, and full native Kira comparisons.
The original models and negative transfer results remain available.
The updated paper uses simpler explanations and comparison tables.

## Complete reduction cost

The [complete-cost study](ML_model_workflow_selection/README.md)
compares models that choose a full reduction strategy from measured time.
It combines seed bounds, saved seed and equation filters, integral ordering,
and the existing temporary database change.
It also compares separate target requests with their joint reduction.
The study includes full native IBP generation and all fallback costs.
It retains the earlier model weights and results.
Its native cases cover seven graph structures at one through three loops.
The restricted vacuum results through twelve loops remain a separate result.
See that folder for the frozen model, test summaries and application commands.

## Models for each graph type

The graph-specific cost study fits separate policy candidates for seven known graph structures.
It compares full exact Kira reductions, including failed attempts and retries.
See [the study guide](ML_model_workflow_selection/type_specialists/README.md) for code, models, tests, inputs, and limits.
The current paper and notes include the mathematical method and measured results.

<!-- BEGIN GRAPH POLICY RESULTS -->

## Completed graph-policy results

The final fit contains 70 candidates for seven graph types.
It uses 544 training cost records and 408 separate validation records.
The reserved test contains 720 timing trials and 43 further application checks.
All checks pass.
The selected-to-native geometric mean time ratio is 0.936849.
Its descriptive interval is [0.886703, 0.987789].
The selected-to-fixed ratio is 0.944077.
Its descriptive interval is [0.899157, 0.986347].
Each graph has equal weight in these aggregate ratios.
A ratio below one means less complete reduction time.
The selected route has a ratio below one in 5 of the seven graph groups.
The inputs use known graph structures and target patterns at new rational profiles.
These results give no speed guarantee for other inputs.

See the study guide for the graph results and limits.

<!-- END GRAPH POLICY RESULTS -->

## Selective seed expansion

The earlier [selective-seeding study](ML_model_workflow_selection/basis_completion/README.md) covers the stated target domain. The reserved test gives 8.8 percent less complete reduction time than the preceding route and 14.8 percent less than native choices in the same test. It contains 720 timing trials and 43 further applications. All pass exact checks. The study uses seven known graphs at one through three loops, new rational parameter profiles, and symbolic dimension. The caller and model are loaded before timing. The report gives per-graph results and descriptive intervals. These gains are not multiplied by earlier results.

## Ordering comparison

The [ordering comparison](ML_model_workflow_selection/ordering_policy/README.md) does not improve the preceding route. That study retained the preceding route. The reserved test gives 1.4 percent more complete reduction time than the preceding route and 15.0 percent less than native choices in the same test. It contains 720 timing trials and 43 further applications. All pass exact checks. The study uses seven known graphs at one through three loops, new rational parameter profiles, and symbolic dimension. The caller and model are loaded before timing. The report gives per-graph results and descriptive intervals. These gains are not multiplied by earlier results.

## Worker-count comparison

The [worker-count study](ML_model_workflow_selection/thread_policy/README.md) compares one, two, and four Kira workers in the same four-core allocation. The reserved comparison gives 1.8 percent less graph-weighted complete time than the preceding route and 15.4 percent less than native choices. Summed batch medians change from 82.21 to 78.73 seconds. It includes 900 timed reductions and 50 additional applications. All pass exact checks. The report separates summed workload time, per-graph effects, and CPU cost. The earlier ordering study remains available and is not the default. That comparison used two cores in its retained application.



<!-- BEGIN HIGHER SCATTERING VERIFICATION -->

## Component and higher-loop verification

The [component and higher-loop study](Kira_comparison/higher_scattering/README.md) tests each decision with matching targets and exact checks.
It preserves the earlier models and results.
It also records connected scattering tests, initialization costs, and incomplete calculations.
Read its summary for the measured contributions and tested domain.

<!-- END HIGHER SCATTERING VERIFICATION -->

<!-- BEGIN COVERAGE STUDY -->
Read [the broader coverage study](Kira_comparison/coverage_study/README.md) for full-basis calculations, all twelve restricted vacuum loop orders, and remaining limits.
<!-- END COVERAGE STUDY -->



<!-- BEGIN EQUATION REFINEMENT -->
The [new equation filter](ML_model_equation_selection/bound_refinement/README.md) is trained on the tuned seed configurations.
Its test separates additional ML savings from fixed seed and exact implementation gains.
Read the graph results, failures, and timing intervals in that guide.
<!-- END EQUATION REFINEMENT -->



<!-- BEGIN BATCH POLICY -->
## Target batch selection

The new [batch policy](ML_model_adaptive_reduction/batch_policy/README.md) chooses which targets Kira reduces together.
Read its guide for the current deployment choice and measured limits.
The [paper](report/report.pdf) and [notes](report/notes.pdf) contain the physics, model, and results.
Earlier studies remain available. Their speedup factors use different workloads and cannot be multiplied.
<!-- END BATCH POLICY -->

<!-- BEGIN BANANA -->
## Combined integral interface

Read [the routing guide](ML_model_adaptive_reduction/massless_banana/README.md) for the exact specialization and native learned workflow.
The formula covers scalar massless banana integrals.
The native models apply within their recorded physical domains.
The paper separates analytic gains, learned gains, failed requests, and regressions.
<!-- END BANANA -->


<!-- BEGIN COST-TRAINED SEED APPLICATION -->
Use `ML_model_seed_selection/cost_geometry/s11_integrated.py` for the updated application.
See [the seed-policy guide](ML_model_seed_selection/cost_geometry/README.md) for inputs, execution, and controls.
The first evolved seed boundary uses 22.3% less time than tuned native Kira on eight planar requests.
It uses 6.5% less time than the initial fixed-width control.
The broader selected workflow uses 22.2% less time than tuned native Kira on 20 matched two-loop requests.
It uses 22.6% less time than the preceding application.
Its comparison with the fixed sparse control gives 3.6% less time.
All successful outputs pass exact coefficient checks.
The fixed sparse control can use a boundary discovered during training.
See `ML_model_seed_selection/cost_geometry/summary.json` for intervals, individual times, failures, and scope.
double_box: Validation retains the fixed sparse boundary.
nonplanar_box: Validation enables the cost predictor.

<!-- END COST-TRAINED SEED APPLICATION -->


<!-- BEGIN JOINT CONFIGURATION RESULTS -->
Use [joint seed choices and scale reuse](ML_model_seed_selection/joint_policy/README.md) for the updated application.
Validation retains the preceding ML application for both graphs.
Neither new joint predictor clears the 2% replacement threshold.
Across 24 reserved first requests, the selected application uses 1.2% less time than the preceding application.
It uses 18.0% less time than tuned native Kira.
Its comparison with the fixed configuration gives 5.7% less time.
The separate three-scale sequences use 64.4% less time than the preceding application without reuse.
Each sequence includes its first Kira solve.
All 480 first-request reductions and 144 sequence requests pass exact checks.
Read `summary.json` for intervals, individual slower requests, and all controls.
These results use known massless two-loop boxes, rational kinematics, symbolic dimension, and supplied masters.
<!-- END JOINT CONFIGURATION RESULTS -->

The current frozen application has a broader test in `Kira_comparison/extended_coverage/`. It records native completion, failures, input limits, and separate exact analytic checks through twelve loops. Read that folder and the new report section for the measured scope.

ML_model_adaptive_reduction/portfolio_policy contains the new family-aware seed-cost models and complete-time comparisons. It also records the higher-loop sector-storage change and scalar full-coordinate checks.
