# Models for each graph type

This study tests separate cost models for seven known integral graphs.
Each model selects a Kira strategy from the target indices.
Kira performs the exact reduction and checks the master basis.
The model does not receive the target coefficients.

The seven graphs are the sunrise, planar box, three-loop vacuum, three-loop ladder, nonplanar box, pentagon, and box with one external virtuality.
The native calculations use one through three loops.
Rational mass and momentum values change between groups.
The dimension stays symbolic.
These cases do not cover arbitrary high-loop scattering graphs.

## Files and sequence

- `s00_study.py` defines the cases and runs the first development probes.
  It also saves compact exact results and enforces the retained-data cap.
- `s01_job.sh` runs one script through the Hoffman scheduler.
  It limits memory and requests one processor.
- `s02_native.py` extends the preceding bounded native runner with Kira's `truncate_sp` option.
  It preserves process, memory, file, and temporary-storage limits.
- `s03_truncate.py` probes three numerator cutoffs on development cases.
- `s04_train_test.py` creates the fixed split, measures complete costs, fits models, and freezes the validation choices.
  Its `test` mode uses the frozen choices on reserved cases.
- `s05_analyze.py` checks all reserved records and makes the result summary and paper plot.
- `s06_reduce.py` applies the saved policy to a target request and a prescribed master basis.
- `s07_finish.py` completes reserved tests, checks the public command, and runs the analysis.
- `s08_validate.py` audits frozen sources, fitted parameters, split separation, exact checks, and storage limits.
- `s09_write_report.py` writes the completed results into the paper, notes, and affected READMEs.
  Review its prose and plots before publication.
- `s10_pair_training.py` repeats mixed-worker training batches, refits the candidates, and freezes the final policies before testing.
- `protocol.json` records the cases, strategies, repetitions, and selection rule before the reserved tests.
- `resource_plan.json` records the storage limit and removed or compressed disposable transport files.
- `pilot_cases.json` records the development cases at profile 61.

Run each command from the project root on Hoffman.
Load the same Python and compiler modules as `s01_job.sh`.
Use the scheduler for all reductions and fitting.

```sh
qsub -o ML_model_workflow_selection/type_specialists/logs/pilot.log ML_model_workflow_selection/type_specialists/s01_job.sh s00_study.py
qsub -hold_jid PILOT_JOB -o ML_model_workflow_selection/type_specialists/logs/truncation.log ML_model_workflow_selection/type_specialists/s01_job.sh s03_truncate.py
qsub -hold_jid TRUNCATION_JOB -o ML_model_workflow_selection/type_specialists/logs/training.log ML_model_workflow_selection/type_specialists/s01_job.sh s04_train_test.py develop
qsub -hold_jid TRAINING_JOB -o ML_model_workflow_selection/type_specialists/logs/pairing.log ML_model_workflow_selection/type_specialists/s01_job.sh s10_pair_training.py
qsub -hold_jid PAIRING_JOB -o ML_model_workflow_selection/type_specialists/logs/test.log ML_model_workflow_selection/type_specialists/s01_job.sh s07_finish.py
```

Replace each job placeholder with the preceding job number.
These dependencies prevent concurrent scientific jobs.
The scripts resume completed records.
They refuse to refit a saved policy after reserved tests.
Preserve completed records when making a new study.

## Physics inputs

The denominator definitions follow the preceding complete-cost study.
The same profile formulas use new values of the profile number.
Development uses 61, training uses 62 and 63, validation uses 64, and reserved testing uses 65 and 66.
All related target batches share the profile split.

The first target shape raises one physical denominator power from one to three.
The second removes the first denominator and, for graphs with at least five physical denominators, the third denominator.
It includes the resulting corner and up to three single-dot targets.
The third puts power minus two on each of the first three available auxiliary denominators.
Graphs without an auxiliary denominator use the first shape again.
The final protocol removes these duplicate target batches.
The training and test sets share graph structures and target patterns.
They use different rational kinematic profiles.

## Strategies and models

The strategies include native choices, maximal target sectors, numerator truncation, a smaller seed region, an expanded seed region, integral ordering five, and the saved equation filter.
Combined sector restriction and numerator truncation form a deterministic control.
Strategies that give identical inputs share one training measurement.
The test runs each method independently, including identical configurations when selected.

Before each attempt, every method raises the positive-index bound to the largest declared sector size.
This prevents invalid input from adding a failed Kira startup to the measured cost.
The development/initial_bounds/ folder preserves the initial sources and 126 affected measurements.
The corrected run retains 288 completed measurements with unchanged inputs.
It repeats the affected measurements, removes equivalent strategies, and uses 544 training and 408 validation records.
No reserved test had started when the correction was made.
A later pairing check repeats eleven training batches whose strategy measurements used different workers.
The development/paired_costs/ folder preserves the replaced measurements and first fitted models.
The final fit uses one worker within each batch comparison.
Validation uses separate data and fixes the policy before reserved tests.

Each graph receives ten fitted candidates.
They are a constant predictor, three regression trees, an ensemble of sixteen bootstrap trees, three ridge regressions, and two nearest-neighbour predictors.
The response is the logarithm of complete time divided by native time.
Complete time includes failed attempts and fallback.
The tree ensemble uses all features at each split.
It is a bagged ensemble, without random feature subsampling.

Validation selects a model and a decision margin separately for each graph.
It enables the model only when it saves at least five percent against the fastest validation control.
Otherwise, the route uses that control.
The fixed choice per graph comes from training costs alone.
A fixed choice can include the older equation filter.
Thus this control can retain an earlier learned component.
The selected route uses native choices for unknown structures or features outside the fitted range.

## Checks and timing

Each attempted reduction has a 120-second limit, a 2,100 MiB process-tree memory limit, and a 32 MiB temporary-storage limit.
Kira uses one processor and fresh node storage.
Every reserved time trial compares exact rational coefficients against an independent native reference.
Additional application checks receive the master indices without reference coefficients.
The comparison checks their outputs after the application finishes.

The timed comparisons use an already loaded Python calling program and fresh Kira processes.
Times include input preparation, model decisions, exact algebra, checks, cleanup, and all retries.
They exclude offline fitting, reference discovery, and saving the benchmark records.
Public command checks also record complete command time with a new Python process.
These command times have no separately matched baseline.

The analysis gives equal weight to each graph.
It uses five-run median times for each reserved batch.
The test order rotates across batches and repetitions.
Each method occupies each run position equally often across the complete reserved suite.
Aggregate intervals resample the seven graph groups.
Per-graph plot bars show the range over two reserved parameter profiles.
These bars are not significance intervals.
The results establish no universal speed guarantee or globally optimal policy.

## Dependencies and application

The runner uses the existing `.tools/kira-workflow/kira` executable, Fermat, Python 3.9, NumPy, SymPy, and Matplotlib.
See the [parent guide](../README.md) for the executable build and preceding models.
The `trained_model/freeze.json` file records the sources, executable, and preceding frozen policy.
Tests verify these records and the saved equation weights.
Keep datasets and trained parameters on Hoffman and GitHub.

The application input contains `case` and `basis`.
The case has `id`, `group`, `split`, `topology_group`, `definition`, `targets`, and `size`.
Use the same family schema as the native runner.
The basis contains integer index vectors.
Do not supply reference coefficients.
Run the application inside a scheduled job with node temporary storage.

```sh
.tools/seed-model/venv/bin/python ML_model_workflow_selection/type_specialists/s06_reduce.py --input request.json --output ML_model_workflow_selection/type_specialists/model_test/request_result.json.gz
```

The output records the selected strategy, exact coefficients, checks, retries, and time.
An incomplete reduction returns a nonzero exit status.
The output must stay inside `model_test/` to enforce the study storage limit.

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

| Graph | Selected model or control | Time / native time |
| --- | --- | ---: |
| Sunrise | Control truncate1 | 0.9831 |
| Planar box | Model tree2 | 0.8576 |
| Vacuum | Control native | 1.0374 |
| Ladder | Model tree1 | 0.8759 |
| Nonplanar box | Model tree2 | 0.8624 |
| Pentagon | Control sector | 0.9511 |
| Virtuality box | Control sector_truncate0 | 1.0081 |

The model_test/summary.json file contains times, decisions, retries, and plot values.
The evidence_validation.json file records the final checks.
Final training and validation records contain 2798.5 seconds of measured reductions.
Fitting the final 70 candidates takes 0.86 seconds.
The label total excludes development, reference construction, and replaced records.
These offline costs remain outside the reserved time ratios.

<!-- END GRAPH POLICY RESULTS -->
