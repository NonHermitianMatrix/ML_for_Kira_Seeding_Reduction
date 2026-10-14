# Selecting Kira ordering

This study selects integral order and propagator permutation before Kira starts.
The seed choices and exact checks use the preceding published method.
All timed calculations include input preparation, model decisions, exact algebra, checks, retries, and cleanup.
Keep raw data and model files on Hoffman and GitHub.

## Code

- `s00_runtime.py` applies the selected settings and restores the preceding route after a failed attempt.
- `s01_study.py` makes exact reference reductions and saves bounded records.
- `s02_native_runner.py` runs Kira with memory, time, and temporary-storage limits.
- `s03_job.sh` runs one stage on one cluster CPU.
- `s04_probe.py` compares settings on separate development inputs.

Use the existing Python environment, Kira binary, and Fermat binary.
Submit the probe with `qsub ML_model_workflow_selection/ordering_policy/s03_job.sh s04_probe.py`.
Development, training, validation, and test profiles remain separate.
The dimension stays symbolic; the external parameters are rational.
The study covers seven known graph structures at one through three loops.
Retain the earlier route for unsupported inputs.
Saved study files have a 16 MiB limit. Each active Kira attempt has a 32 MiB temporary-storage limit.

## Training and application

- `s05_fit.py` fits seventy complete-cost predictors and selects them on validation inputs.
- `s06_test.py` compares frozen policies on reserved inputs.
- `s07_reduce.py` applies the frozen policy to a case and a prescribed master basis.
- `s08_analyze.py` checks test records and makes the result plot.
- `s09_pipeline.py` tests one combined ordering per development batch, selects candidates, then trains, freezes, tests, and checks the application.
- `s10_public_checks.py` checks seven fresh-process applications without target coefficient inputs.
- `s11_validate.py` checks split separation, exact results, source versions, resource limits, and folder guides.

After development finishes, submit `s14_pipeline.py` with `s03_job.sh`.
Use `s07_reduce.py --input INPUT.json --output ML_model_workflow_selection/ordering_policy/model_test/OUTPUT.json.gz` for an application.
The input contains `case` and `basis`. The case contains a family definition and integer target indices.
The output contains exact coefficients, the chosen strategy, total time, checks, and resource peaks.
The application does not receive reference coefficients.
The wrapper uses one CPU and one active Kira process. It does not require a new Kira build.

## Report and evidence

- `s12_write_report.py` writes the measured results to the paper and notes.
- `s13_finish.py` validates the evidence, updates guides, and builds both PDFs.
- `ordering_policy_appendix.tex` gives the scientific definitions and derivations.
- `resource_plan.json` reserves space for the study, reports, temporary files, and Git publication.
- `development_cases.json` lists all development cases and candidates.
- `candidate_selection.json` records candidate selection before training.
- `protocol.json` records separate inputs and measurement rules.
- `evidence_validation.json` records the completed evidence checks.

The supported `s14_pipeline.py` entry point also builds the documents after testing.
The report gives the measured gains, regressions, and supported input domain.
The prediction uses target features and graph structure. It does not use the target solution.

`joint_development.json` records the combined settings tested before training.

## Explicit module loading

Use `s14_pipeline.py` for the complete pipeline after the development probe.
It loads this study's analysis and public-check modules by their exact paths.
The saved `s09_pipeline.py` remains unchanged because its version is part of the model freeze.
An import with the same name previously selected the older generalization summary module.
This affected summary dispatch after the timed tests. It did not change training, frozen decisions, or timed reduction records.
The two regenerated historical summary outputs were restored from the preceding publication.
The `summary_dispatch_repair.json` file records this restoration.
Use `s14_pipeline.py --finish-only` to validate existing test records and rebuild summaries and documents.
This option preserves the completed public applications and does not repeat the timing experiment.

## Completed comparison

All 720 timed reductions and 43 further applications pass exact checks. The selected method gives 1.4 percent more full time than the preceding method and 15.0 percent less than native choices. These are geometric means with equal graph weights. See `model_test/summary.json` and the paper for each graph, all regressions, timings, and limits. The test covers known graphs and target patterns with new parameter profiles.
