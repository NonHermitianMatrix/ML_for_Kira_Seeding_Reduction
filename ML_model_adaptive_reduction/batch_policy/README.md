# Target batch selection

This study trains a model to choose which targets Kira reduces together.
Each target is an integral index vector in one physical family.
The five choices are one batch, equal numerator ranks, equal extra denominator
powers, equal sectors, and consecutive groups of three targets.
A sixth candidate keeps one batch and disables the equation filter.
Each part uses native integration-by-parts equations and exact algebra.
The existing equation filter can run within its checked domain.

## Current result

The reserved comparison has 96 matched nontrivial batches.
The selected-to-previous complete-time ratio is 1.014613.
The ratio to fixed partitions with the same filters is 1.008069.
The ratio to separately tuned fixed partitions with all ML disabled is 0.998825.
Validation enables the new predictor: False.
Read `summary.json` for each graph, timing intervals, failures, and completion counts.
Its `validation_candidate_bound` sums each validation batch's smallest recorded candidate cost.
This value requires future timing information. It does not describe a deployed predictor.
All successful reductions pass exact coefficient checks.
These results concern known structures at one through four loops.
The calculation receives a master basis. It does not discover that basis during timing.

## Use

Run on a Hoffman compute node from the project root.
Supply a case file and a basis file in JSON format.
The case has a physical family definition and a list of target index vectors.
The required top-level fields are `id`, `size`, `targets`, and `definition`.
Native run labels are optional. The adapter matches known graph labels from the physical definition.
Unknown graphs keep native settings. The application tests use this minimal input format.
The definition includes `physical_propagators`, `top_level_sectors`, and the propagator and kinematic data.
Use a case entry from `model_test/protocol.json` as the schema.
The basis file is a list of integer index vectors.
The live interface receives no reference coefficients.

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/batch_policy/s16_deployment.py --case CASE.json --basis BASIS.json --output RESULT.json.gz --method learned
```

`learned` uses the frozen deployment choice.
`fixed` uses a fixed partition per graph with the equation filters available.
`fixed_off` uses separately tuned fixed partitions with all ML disabled.
`previous` keeps the full batch and uses the previous filter policy.
`off` keeps the full batch and disables all ML.
The interface checks target and basis indices before reduction.
Unknown structures use one batch and native seed bounds.
An insufficient equation set triggers exact recovery within the time limit.
A request that exhausts its limit returns failure.

## Execution order

1. Read the saved development records and their original source snapshot.
2. Run `s02_collect.py training` to measure training costs.
3. Run `s02_collect.py validation` to measure separate validation costs.
4. Run `s02_collect.py validation_off` to tune controls with all ML disabled.
5. Run `s04_fit.py` to fit models, select settings, and freeze the policy.
6. Run `s05_test.py` to compare fresh reserved requests.
7. Run `s11_finish.py` to check applications, audit answers, and build documents.

Submit each stage with `s03_job.sh`. It sets the worker and process limits.
`s06_pipeline.py` performs steps 2 through 6 in order.
It resumes saved measurements. It does not overwrite completed trial files.
Use a new study directory and new profiles for a changed scientific policy.
The published test inputs must not become tuning inputs for this frozen comparison.
The initial development stage used five actions. Its snapshot preserves that version.
The final six-action program does not overwrite the initial development protocol.

## Code and evidence

`s00_runtime.py` defines partitions, prediction, validation, and native execution.
`s01_cases.py` defines physical requests and builds common-basis references.
`s02_collect.py` measures every candidate and retains failed attempts.
`s04_fit.py` compares 18 cost predictors and four prediction margins.
`s05_test.py` runs five methods with rotated execution order.
`s07_analyze.py` checks coefficients and makes the timing plot.
`s08_application.py` times fresh Python processes and exact checks.
`s09_document.py` writes the paper and notes sections.
`s10_readmes.py` maintains these guides.
`s11_finish.py` runs the final checks and PDF build.
`s12_parallel.py` divides independent graphs between two workers.
It preserves the original candidate order and complete-time measurements.
Each reserved batch keeps all methods and repetitions on one worker.
`parallel_execution.json` fixes these graph groups and source files before testing.
`parallel_jobs.json` records the preserved measurements and scheduler jobs.
Its `fit_submit` mode contains the finish-job identifier for this recorded run.
Use the ordinary numbered stages above for a separate reproduction.
To resume this run, use its recorded worker modes and job dependencies.
`s13_reserved_workers.py` assigns the reserved graph groups to four workers.
It uses the same test loop and timers. It changes only the graph assignment.
`reserved_execution.json` fixes this assignment before model fitting and testing.
The fitting job froze the model after both collection jobs finished.
Its attempt to submit tests failed because its compute-node environment could not find `qsub`.
`s15_resume_tests.py` submitted the unchanged frozen tests from the login node.
It also submitted the final checks with dependencies on all four test workers.
`submission_recovery.json` records this scheduling correction. Both failed job logs remain available.
No training, model selection, or test protocol changed during this correction.
`s14_status.py` shows stage counts, current model settings, and this study's registered jobs.
Run it from the project environment to check progress without listing unrelated jobs.
`s16_deployment.py --prepare` writes the compact deployment policy from the frozen model.
It removes unused tree arrays when validation disables the predictor.
It checks identical choices on all training, validation, and reserved inputs without reading reserved timing outcomes.
`deployment_checks.json` records these checks and both file sizes.
The reserved timing comparison keeps the original `s00_runtime.py` implementation.
The separate application tests and combined interface use `s16_deployment.py`.
`s17_application_stage.py` can run the fixed application subset after its references are ready.
It requires at least one completed reserved worker before using one additional worker.
The final document job depends on both the reserved tests and this application stage.
Run `s18_submit_applications.py` on the login node to submit that stage after its references are complete.
`application_job.json` records the fixed requests, resource limit, and added document-job dependency.
`s19_resume_interrupted.py` preserves partial comparisons and submits four replacement workers from the login node.
It retains complete batches and repeats every method for an unfinished batch.
It balances whole batches from validation costs only.
`s20_resume_workers.py` changes only the assigned case list in the frozen runner.
It preserves the original timers, method rotation, exact checks, and recovery rules.
`resumed_execution.json` seals these assignments and the unchanged scientific sources.
`interruption_recovery.json` lists complete batches, remaining work, and archived records.
`interrupted_trials/` preserves four partial timings and the original worker logs.
These partial timings do not enter the final ratios. The final audit checks their exact results separately.
`resumed_jobs.json` records the four-hour allocations requested at submission.
`completed_job_accounting.json` records successful worker exits and their reported peak memory use.
`document_build_recovery.json` records the correction to the notes-update script and the replacement document job.
The correction preserves all earlier included sections. It changes no scientific result.
`batch_policy_appendix.tex` defines the method and derives the merge rule.
`fixed_inputs.json` identifies the previous frozen filters and seed settings.
`resource_plan.json` records the storage budget.
`validation.json` records final checks and document hashes.

Development uses profile 701. Training uses 711. Validation uses 712.
Reserved testing uses 721 and 722. Graph structures recur across these splits.
Some index sets recur at different rational kinematics. The summary records this overlap.
Weights, thresholds, and the existing equation filters remain fixed during testing.
Training uses two repetitions, validation uses three, and testing uses five.
Candidate labels share a measured cost only when their ordered parts and filter setting are identical.
Each protocol records this mapping. Shared labels do not count as separate timed calculations.
When all parts are equivalent and no filter applies, the interface skips prediction and uses one batch.
Failed training candidates receive a cost penalty of at least 300 seconds.
This penalty is a learning target, not a measured completion time.

The timer includes policy loading, prediction, equation generation, exact algebra,
recovery, coefficient checks, and cleanup. Repeated trials exclude initial imports.
The application check includes a new process and its imports and output.
Reference construction and offline training remain outside deployment timing.
The summary also retains equation and row-insertion counters from the native logs.
It sums reported passes and retries, then takes each batch's median.
These counters do not measure the total number of arithmetic operations.

## Dependencies and limits

Use the existing `.tools/seed-model/venv` environment and `.tools/kira-parametric/kira`.
The model fit uses NumPy and scikit-learn. Plotting uses Matplotlib.
The live predictor reads exported tree arrays and needs no scikit-learn import.
The shared native runner provides exact Kira execution and resource guards.

The scheduler requests one worker and 8 GiB of memory.
Each native process has a 6 GiB address-space limit and 32 MiB of scratch space.
A complete request has 150 seconds. Each attempt has at most 60 seconds.
Reference attempts have at most 90 seconds. Retained study files have a 32 MiB cap.
The combined local and Hoffman project limit remains 10 GB.
Scientific work, document preview, and publication use separate storage phases.
Training and validation use at most two native workers.
Reserved tests use at most four, with at most 128 MiB of aggregate scratch space.
Application checks may use a freed worker while the remaining reserved tests finish.
The total number of simultaneous native workers stays at most four.
`test_queue_adjustment.json` records the shorter one-hour worker request used to reduce queue delay.
The 8 GiB memory request and native memory guards remain in place.
`test_queue_access.json` permits either of two standard shared CPU queues.
Each batch still keeps all methods and repetitions on the same worker.
`test_runtime_extension.json` records accepted requests to extend the running allocations.
The execution service still enforced their original one-hour limits and stopped two workers.
`interrupted_job_accounting.json` records both time-limit exits and memory peaks near 1 GiB.
The interruption did not result from exhausted memory.
Complete batches stay unchanged. Each unfinished batch repeats as a whole on one new worker.
The new workers request four hours at submission and retain the native attempt limits and memory guards.
The final document and publication stages start after these workers finish.
The first main job lost its memory request after a scheduler resource edit.
It was stopped, its 57 complete training records were checked, and training resumed with an explicit 8 GiB request.
`scheduler_correction.json` records this correction. The original log remains available.
When changing scheduler resources, include both the time and memory requests.
Before fitting, the retained-data cap increased from 24 to 32 MiB.
The source snapshot and `storage_guard_revision.json` record this change.
The calculation, candidate actions, and timers stayed unchanged.
Rebuildable compiler objects were removed to preserve project storage headroom.
All executables, source files, scientific data, and earlier measurements were retained.

The native interface accepts at most 31 integral indices.
The current cost model supports only its recorded physical structures and power ranges.
The earlier one-through-twelve-loop vacuum recurrence remains a separate result.
No finite test establishes the fastest method for every integral type or loop order.
