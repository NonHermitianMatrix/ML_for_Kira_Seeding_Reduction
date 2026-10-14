# Complete-cost selection for Kira

This folder trains models to select a complete reduction strategy.
The target is lower full reduction time with exact coefficients.
The model can select seed bounds, a seed filter, an equation filter, or an integral ordering.
Native algebra checks the selected equations against a supplied master basis.
If a strategy fails, the driver retries with native choices.
All retry costs remain in the measured time.

The integration combines early equation filtering with the existing temporary database improvement.
Earlier equation-filter builds did not link that database change.
The temporary database change applies only inside a marked disposable calculation directory.
A failed calculation must restart in a new directory.
The driver saves the final coefficients before it removes the directory.
The build keeps all earlier executables.

## Data and models

`cases.json` gives all propagators, scalar products, targets and split assignments.
The cases use seven existing graph structures at new parameter points.
They include rational kinematics and symbolic scattering kinematics.
Dimension remains symbolic.
The native calculations cover one, two and three loops.
The separate restricted vacuum method through twelve loops remains in
[the exact backend](../ML_model_equation_selection/exact_backend/README.md).
These data do not cover arbitrary scattering graphs at high loop orders.

Training uses 31 batches. Validation uses 17 batches. Testing uses 31 batches.
Training has three timing repetitions per strategy.
Validation has three repetitions, and testing has five repetitions.
The test parameter points are not used for training or strategy selection.
Graphs are shared across the splits.
The study therefore tests new inputs within known structures.

The twelve candidate models include a constant predictor, six regression trees, three ridge-regression models, and two nearest-neighbour models.
Ridge regression fits linear coefficients with a penalty on their size.
The target label is the logarithm of a complete-time ratio.
The denominator is the integrated native strategy.
The feature list is in `trained_model/candidates.json`.
Validation selects the model and a minimum predicted saving.
The selected model is frozen before the test.
Validation selects ridge regression with penalty 10 and saving margin zero.
Its validation ratio to integrated native choices is 0.992688.
Integrated native choices are also the best fixed strategy from training.
These validation values do not replace the reserved test.
The older seed and equation trees retain their saved weights.
For structures without a new seed tree, the seed candidate uses native choices.
The row-selection model remains outside this route.

The seven strategies are `fixed`, `tight`, `dots`, `equation`, `seed`, `order5`, and `expanded`.
`fixed` uses native decisions with the combined integration.
`tight` reduces the maximum positive index sum, numerator rank, and dot count by one.
`dots` reduces the positive index sum and dot count by one.
Both reductions keep each bound at least zero.
`equation` and `seed` apply the saved trees before coefficient construction.
`order5` selects Kira integral ordering five.
`expanded` increases all three initial seed bounds by one.
This can avoid a failed initial reduction.
All strategies use ordering one unless their name specifies another ordering.

## Execution

Run these commands from the project root on Hoffman.
The wrapper loads GCC 9.5.0 and Python 3.9.6.
The Python environment supplies NumPy, SymPy and Matplotlib.
The build uses the existing Kira objects and libraries.
A new installation must first build [the early equation integration](../ML_model_equation_selection/early_generation/README.md)
and [the guarded database implementation](../Kira_comparison/integrated_runtime/README.md).
`s04_build.py` reads the saved link command and combines their object files.
The executable and tool libraries stay outside Git.

1. Submit `qsub ML_model_workflow_selection/s01_job.sh s00_pilot.py` for the initial development pilot.
2. Submit `qsub ML_model_workflow_selection/s01_job.sh s06_develop.py` after the pilot ends.
3. Submit `qsub ML_model_workflow_selection/s01_job.sh s11_refit.py` after development.
   This adds less constrained tree fits before any reserved test.
   Read `trained_model/freeze.json` after this job completes.
4. Submit `qsub ML_model_workflow_selection/s01_job.sh s10_finish.py` for tests, analysis and joint-request comparisons.
5. Submit `qsub ML_model_workflow_selection/s01_job.sh s14_check_requests.py` for the learned joint application and final plot.
6. Submit `qsub ML_model_workflow_selection/s01_job.sh s17_check_best.py` for the default joint application.

Run only one scientific job at a time.
Existing completed records are reused on restart.
Do not change a frozen model during its reserved test.
Keep old test records before defining a new study.

## Code

`s00_pilot.py` compares eight integral orderings and stronger equation thresholds on earlier training cases.
It also supplies bounded compressed record writing for this folder.
`s01_job.sh` runs one script under scheduler memory and time limits.
`s02_run.py` extends the earlier native driver with explicit seed bounds and the combined executable.
Its `run` function creates fresh inputs, runs Kira, checks the basis and coefficients, and removes temporary files.
Its legacy command-line interface remains available for the earlier generalization cases.
Use `s08_reduce.py` for this model's application interface.
`s03_bounds.py` probes smaller seed regions on earlier training cases.
`s04_build.py` links the early equation integration with the guarded database object.
It writes `build.json` and the executable under `.tools/kira-workflow/`.
`s05_study.py` defines the cases, records costs, fits models, selects settings, freezes them, and runs reserved tests.
Its actions are `prepare`, `collect`, `train`, `validate`, `test`, and `all`.
`s06_develop.py` runs the bounds pilot, build, training, validation, and freeze in sequence.
`s07_analyze.py` checks reserved records and writes the summary and complete-time plot.
It does not change a trained model.
`s08_reduce.py` applies the saved selector to a supplied case and master basis.
Its required arguments are `--input`, `--basis`, and `--output`.
`s09_batching.py` compares two separate target requests with their joint reduction.
It fixes the requests before testing and retains the frozen model.
`s10_finish.py` runs reserved tests, public application checks, analysis, and the joint-request comparison in sequence.
`s11_refit.py` adds three trees that allow one training batch per child.
It selects the final model from validation costs and preserves the earlier fit.
It stops if a reserved test has already started.
Use `qsub ML_model_workflow_selection/s01_job.sh s10_finish.py` after the final refit to run all reserved comparisons.
`s12_plot_batching.py` plots the completed joint-request results.
`s13_reduce_requests.py` applies the model to compatible requests and returns their separate coefficient rows.
Its arguments are `--requests`, `--basis`, and `--output`.
The requests file is a JSON list of case objects with the same exact family definition.
`s14_check_requests.py` checks ten joint applications against independent native coefficients.
Run it after `s10_finish.py`. It also generates the joint-request plot.
`s15_validate_evidence.py` checks completed records and frozen settings without new reductions.
It writes `evidence_validation.json`. Each joint application check runs it last.
`s16_reduce_best.py` is the standard joint-request command.
It uses the best fixed strategy from training. The `--learned` option activates the frozen cost model.
Its other arguments are `--requests`, `--basis`, and `--output`.
`s17_check_best.py` checks ten applications of the default command against independent coefficients.

The application input is a case object with the same fields as one entry in `cases.json`.
The basis input is a JSON list of master index vectors.
The output must be inside `model_test/`.
The application does not receive target reference coefficients.
Unsupported structures use the integrated native strategy.
The native solver still determines their results.
The resource limits can stop a difficult calculation; they do not guarantee completion for every input.

## Records and limits

`development/` preserves the initial probes.
`references/` stores native reductions from enlarged seed regions.
`training/` stores complete-time labels and exact checks.
`validation/` stores strategy comparisons used to select the model.
`trained_model/` stores all candidate models and the selected settings.
`model_test/` stores reserved trials, applications without reference answers, and the summary.
`logs/` stores scheduler messages, including development failures and their corrected runs.
`request_batching/` stores the joint-request protocol, exact reductions, and summary.

Each gzip record contains JSON.
The `attempts` list records every solver call, including unsuccessful calls.
The final successful attempt contains the exact target-to-master coefficients.
`complete_seconds` includes preparation, inference, Kira, exact checks, cleanup, and fallback.
Offline reference discovery, training, and evidence archiving are outside this timer.
The Python controller stays running between trials, while each Kira call starts a new process.
The test compares the previous native executable, integrated native choices, the best fixed strategy, and learned choices.
This separates integration gains from gains due to the model.

`resource_plan.json` gives the combined storage budget.
Retained files in this folder must stay below 40 MiB.
Each Kira attempt has a 120-second limit, a 32 MiB temporary-file limit, and a 2,100 MiB process-tree memory limit.
The complete project must stay below 10,000,000,000 bytes across Hoffman and the local report copy.
Generated scientific records and fitted models stay on Hoffman and GitHub.

See `model_test/summary.json` for completed results.
See [the paper](../report/report.pdf) and [the notes](../report/notes.pdf) for the scientific account.

## Main reserved result

All 620 timed reductions and 31 basis-only applications pass exact checks.
The learned-to-previous-native time ratio is 0.990340.
The learned-to-integrated-native ratio is 0.996494, with interval [0.987471, 1.006953].
The learned-to-best-fixed ratio is 1.002568, with interval [0.997865, 1.008116].
These controls establish no added full-time saving from the learned choice.
The standard command therefore retains the best fixed training strategy.
The fitted models remain available through the learned option and the comparison commands.
Use the joint-request summary for its separate time comparisons.

## Standard application

Use `s16_reduce_best.py` for compatible requests with a supplied master basis.
It groups the targets, uses the best fixed training strategy, and returns each request's coefficient rows.
Use `--learned` only to select the frozen cost model for comparison.
For repeated use in one Python process, call `s13_reduce_requests.reduce_requests(requests, basis, use_model=False)`.
The running-controller timing results apply to this repeated-use setting.
Cold command times are recorded separately in the application checks.
These checks do not provide a matched cold-start speedup comparison.

## Joint-request result

All 200 joint-request comparisons pass exact coefficient checks.
The standard joint route has time ratio 0.517474 to two separate native reductions.
Its descriptive interval is [0.507293, 0.534572].
This is 48.3 percent less time, or about 1.93 times faster.
All seven graph groups benefit from the shared reduction.
The learned-to-joint-integrated ratio is 0.995542, with interval [0.980961, 1.005803].
The comparison establishes no further saving from the learned choice over that control.
The measurements require two compatible requests available together.
They do not establish this saving for an isolated arbitrary target.

The final audit checks 651 training records, 357 validation records, 820 timed reserved workflows and 61 basis-only applications.
The application total includes 31 main checks and ten checks of each public command.
The figures and report values come from the saved results.
No reserved test changes the model coefficients.

## Separate policies for seven graphs

The [type_specialists guide](type_specialists/README.md) describes the completed cost-model study.
It compares ten predictors for each graph and nine reduction strategies.
The public application selects a fitted model or a validation control and then calls exact Kira.
The new study preserves the preceding models and test records.
Its native inputs use one through three loops and fresh rational parameter profiles.

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
