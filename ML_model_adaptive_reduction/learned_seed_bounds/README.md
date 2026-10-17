# Learned seed bounds

This study selects seed limits before Kira generates IBP equations.
IBP means integration by parts.
A seed is an integral index vector used to generate these identities.
The model predicts the complete cost of ten settings.
It uses the target indices and the graph structure.
It receives no answer coefficients.
Kira performs the exact algebra and checks the supplied master basis.
An insufficient first choice triggers native bounds and then expanded bounds.

The selected model is `random_forest_d8`.
The test has 68 matched nontrivial batches.
The sum of their median times is 164.926115 s for native bounds.
It is 119.716730 s for the tuned fixed control.
It is 119.080958 s for the learned choice.
The learned-to-control ratios are 0.722026 and 0.994689.
A ratio below one means less time.
The interval against tuned fixed settings includes equal time.
The extra learned gain is not reliable on this test.
Read `summary.json` for each graph, failed requests, and timing intervals.
The controls use no learned seed, row, or equation choices.
All methods use the same exact executable.

## Scope

The inputs use ten graph structures at one through four loops.
Kinematic values are rational numbers. The dimension remains symbolic.
Training, validation, and test use separate parameter profiles.
They share graph structures and target patterns.
Some target patterns coincide when no auxiliary numerator exists.
The test does not establish performance for arbitrary new graphs.
The timed reduction starts with a supplied master basis.
It includes equation generation, algebra, parameter loading, prediction, checks, and retries.
The repeated timer excludes initial Python imports and reference construction.
A low score changes the seed choice. Kira checks the resulting reduction.
It reports failure if the bounded recovery attempts do not finish.

## Use the fitted model

Run from the project root in a scheduled Hoffman job.
Supply a case JSON file and a basis JSON file.
The case schema matches an entry in `protocol.json`.
The basis is a list of integer index vectors.
Use the same family and index length for targets and masters.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/learned_seed_bounds/s01_runtime.py --case CASE.json --basis BASIS.json --output RESULT.json.gz --method learned
```

`native` and `fixed` select the two controls.
`learned` uses the saved model and the domain check.
Unknown structures or target complexity outside the saved ranges use native bounds.
The guard checks target count, maximum dots, rank, absolute index, and positive-index sum.
It allows target positions and mean loop-incidence features to change.
The result contains the chosen action, all attempts, times, and exact coefficients.
The application does not require reference coefficients.
The test supplies them only to the check after each reduction.

## Reproduce the study

1. Read `resource_plan.json` and `protocol.json`.
2. Run `s02_development.py` for the saved development comparison.
3. Run `s04_collect.py` for training and validation cost records.
4. Run `s05_train.py` to fit and select the model.
5. Run `s06_test.py` for the frozen reserved comparison.
6. Run `s08_analyze.py` for the summary and plots.
7. Run `s13_finish.py` for the final checks, guides, and documents.

Use `qsub s03_job.sh SCRIPT.py` from the project root with the full script path for the job wrapper.
For example, use `qsub ML_model_adaptive_reduction/learned_seed_bounds/s03_job.sh s04_collect.py`.
The collector resumes from complete result files.
Do not change a frozen model and reuse its test files.
Use a new folder and new reserved inputs for a changed scientific method.

## Code and records

- `s00_inputs.py` defines physical families, target patterns, features, and seed settings.
- `s01_runtime.py` runs the exact reduction and the optional learned choice.
- `s02_development.py` checks candidate settings on development inputs.
- `s03_job.sh` sets scheduler, thread, and memory limits.
- `s04_collect.py` fixes the split and collects complete cost labels.
- `s05_train.py` compares 30 tree and neural models and four decision gates.
- `s06_test.py` rotates three methods through five reserved repetitions.
- `s07_pipeline.py` runs fitting and testing in separate processes.
- `s08_analyze.py` writes checked timing summaries and two figures.
- `s09_report.py` writes the scientific description in both documents.
- `s10_secondary.py` checks fresh application launches against the previous application.
- `s11_readmes.py` writes these folder guides.
- `s12_audit.py` checks saved coefficients, split integrity, and control settings.
- `s13_finish.py` completes analysis, documentation, and PDF checks.
- `protocol.json` fixes the inputs, controls, limits, and primary comparison.
- `resource_plan.json` records the storage reserve and job limits.
- `baseline_basis_check.json` records the source check of early master admission.
- `jobs.json` records scheduler job numbers.
- `summary.json` records all test outcomes and matched aggregate times.
- `validation.json` records the final publication checks.
- Log files record progress and failures.

Child folders contain development records, references, training costs, validation costs, the fitted model, and reserved tests.
Each child folder has its own guide.
The code depends on the existing exact driver `../s23_parametric_runner.py` and `.tools/kira-parametric/kira`.
Fitting uses the existing NumPy and scikit-learn environment.
Analysis uses Matplotlib. Exact coefficient checks use SymPy when needed.
Live prediction uses Python and the saved parameters. It does not load scikit-learn.

## Limits

Use one project job with two allocated cores and 8 GiB of memory.
Each Kira attempt uses one worker.
The address-space limit is 6 GiB. The process-tree limit is 5,200 MiB.
Each attempt has a 32 MiB scratch limit and a 90 s allowance.
Reference attempts have a 120 s allowance.
The driver reserves ten seconds for parsing and cleanup.
The study retains at most 24 MiB of result data.
Keep the complete project below 10,000,000,000 bytes.
Keep generated research data on Hoffman and GitHub.
The report and notes also have local copies.
