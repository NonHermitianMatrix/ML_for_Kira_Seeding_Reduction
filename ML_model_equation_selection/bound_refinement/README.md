# Equation filtering after seed tuning

This model decides which IBP equations Kira constructs.
IBP means integration by parts.
A candidate is one seed integral with one IBP or Lorentz-invariance operator.
The model reads index information before symbolic coefficient construction.
It returns a tree leaf score for each candidate.
The underlying equation score is a training frequency. It is not a calibrated confidence guarantee.
A whole-seed variant keeps every operator when any operator receives a high score.
Its equivalent compiled decision returns 0 or 1.
Kira retains a candidate when its score meets the selected threshold.
Kira then performs exact elimination and checks the supplied master basis.
An insufficient equation set triggers a complete retry without the filter.

## Measured result

The reserved test has 68 matched nontrivial batches.
Validation enables filtering on 32 of those batches.
Their total median time changes from 91.707198 s to 84.383911 s.
Across all matched batches, time changes from 153.936670 s to 146.586087 s.
The ratios are 0.920145 for active batches and 0.952249 for all matched batches.
Read `summary.json` for each graph, intervals, failures, and retries.
Read `index_transfer/summary.json` for the separate check with new target-index batches.
Each of those batches contains an individual index vector absent from training and validation.
The control disables all learned choices.
It uses the same fixed seed settings, exact code, master basis, and worker count.
This isolates the additional effect of the equation model.

## Use

Run on a Hoffman compute node from the project root.
Use the existing Python environment and Kira executable.
Supply a case file and a master basis file in JSON format.
A case follows the schema in `model_test/protocol.json`.
The basis is a list of integer integral-index vectors.
The live application requires no reference coefficients.

```bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/bound_refinement/s07_reduce.py --case CASE.json --basis BASIS.json --output RESULT.json.gz --method learned
```

Use `--method off` to disable the filter while keeping the same seed policy.
The domain check compares the ordered propagators, momenta, sectors, and zero patterns.
It also checks the target-count and index-power ranges.
Unknown inputs use an exact fallback configuration.
Every attempt must reduce all requested targets into the supplied basis.
The output stores exact coefficients, choices, times, and all recovery attempts.

## Reproduce

1. Read the seed-bound study in `../../ML_model_adaptive_reduction/learned_seed_bounds`.
2. Run `s00_probe.py` to test the older equation filters with tuned seed limits.
3. Run `s02_train.py` to collect labels and fit the shared trees.
4. Run `s03_refine.py validate` to compare complete validation costs.
5. Run `s03_refine.py test` after the model is frozen.
6. Run `s09_finish.py` to complete the separate tests, analysis, guides, and both documents.

The final script runs `s15_index_transfer.py` and `s12_application.py` before analysis.
It then runs `s05_analyze.py`, `s06_document.py`, and `s08_readmes.py`.
Those scripts check saved coefficients, draw the plot, and write the report and guides.
Run them separately only after their input tests are complete.

`s01_job.sh` sets cluster and process limits.
`s10_fit_graph.py` also fits separate trees for each graph before complete-cost validation.
`s11_parity.py` checks compiled feature construction and tree decisions against the saved validation rows.
Its small compiled check runs in temporary node storage and is removed after the check.
`s13_seed_filter.py` derives whole-seed choices from the trained equation scores.
`s14_check_union.py` checks this exact decision transformation on finite feature grids.
Validation compares these choices with the individual equation filters.
`s15_index_transfer.py` tests the unchanged policy at profiles 605 and 606.
It excludes index batches already present in training or validation.
It also requires an individual unseen target vector and removes repeated batches within each profile.
The selection uses the original validation choices, without primary test timings.
`s12_application.py` compares fresh application processes with and without the frozen filter.
It includes startup, output storage, process exit, and independent coefficient checks.
`s04_pipeline.py` runs collection, fitting, validation, and the reserved test.
It skips testing if no filter meets the validation saving requirement.
Run scripts through the scheduler. Do not run reductions on a login node.
For example, submit `qsub ML_model_equation_selection/bound_refinement/s01_job.sh s04_pipeline.py`.
Do not change a frozen model and reuse its test results.
Use new reserved inputs for a changed method.

## Data and model

Training uses kinematic profiles 511 and 512.
Validation uses profile 513. The new test uses profiles 525 and 526.
Graph structures and target patterns are shared across these sets.
Some primary test index patterns also occur in training.
The separate index-transfer test excludes those batches and requires at least one new individual target vector.
The dimension remains symbolic. The kinematic values are rational numbers.
The scope contains ten graph structures at one through four loops.
The test does not establish transfer to every topology or higher loop order.

Each label records native selected integral-support membership.
Collection uses `.tools/kira-equation-selection/kira-lazy`, which can export training records.
Every collected reduction must match the independent exact reference.
Both timing controls use the same current `.tools/kira-parametric/kira` executable.
Support is the set of integrals with nonzero coefficients in an equation.
This is a proxy for usefulness. It is not a proof that an equation is necessary.
Each batch retains at most 2,000 sampled records per class.
Each sample stores a 0/1 label, an inverse sampling weight, and seventeen feature values.
The `features` list gives their order.
The `candidate_keys` list pairs each seed index vector with its operator index.
The `source_rows` value records the native candidate count.
Training divides each sampling weight by this count.
Inverse sampling weights preserve class proportions.
Each batch has equal total weight during fitting.
Eight shared and eight graph-specific configurations use depths 6, 10, 14, and 18, with minimum leaf populations 4 and 16.
Each tree has at most 4,096 leaves.
Only 17 features available before coefficient construction enter the model.
Validation shortlists thresholds by reference recall and retained fraction.
Three complete-cost repetitions then select the filter for each graph.
The policy enables it only when validation saves at least 5 percent.

The frozen file records model hashes, graph choices, thresholds, and domain limits.
The final check verifies every selected model against the compiled node and path-depth limits.
Read `trained_model/runtime_structure.json` for these results.
Model text files contain the tree nodes read by Kira.
Each node gives a feature, threshold, child indices, and leaf score.
Derived seed decisions can share descendant nodes. They implement the same logical choice as the source scores.
The first line gives the number of nodes. A feature value of -1 denotes a leaf.
Compressed model JSON files explain the fit and feature mapping.

## Resource limits

Use one project calculation job at a time with an 8 GiB allocation.
The live reductions and model fitting each use one CPU worker.
The pipeline allocation was reduced to one CPU slot with 8 GiB while queued.
The scheduler wrapper keeps the portable two-slot, 4 GiB-per-slot request.
Each Kira attempt has a 6 GiB address-space limit and a 5,200 MiB process-tree limit.
Each attempt has 32 MiB of scratch space and a 90 s allowance.
Reference attempts have a 120 s allowance.
The driver reserves ten seconds for parsing and cleanup.
The two new studies share a 32 MiB retained-data limit.
The complete project must remain below 10,000,000,000 bytes.
Keep generated research data on Hoffman and GitHub only.
The report and notes also have local copies.

Training uses Python 3.9.6, NumPy 1.22.2, and scikit-learn 0.24.2.
The code also uses SymPy and Matplotlib.
Read [the exact-preparation guide](../../ML_model_adaptive_reduction/parametric_preparation/README.md) for the current Kira build.
Read [the early-generation guide](../early_generation/README.md) for the collection build and the equation hook.
Live tree prediction runs inside the existing Kira executable.
The runtime uses `../../ML_model_adaptive_reduction/s23_parametric_runner.py`.
It shares the exact preparation flags from the seed-bound study.
