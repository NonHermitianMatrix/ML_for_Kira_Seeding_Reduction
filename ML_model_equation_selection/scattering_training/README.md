# Training for scattering integrals

This study adds training examples from three scattering structures.
They are the massless nonplanar two-loop box, massless pentagon, and box with one external virtuality.
The earlier equation tree had no training examples from these structures.
Its earlier transfer tests remain in [generalization](../../Kira_comparison/generalization/README.md).

The study fits one seed tree and one equation tree for each structure.
The original neural networks and equation trees remain unchanged.
The seed trees omit the operator feature.
All operators of a seed therefore receive the same score.
The equation trees can select individual operators.
Both models act before symbolic coefficient construction in the existing Kira integration.
Kira keeps its native elimination order and row choices.

Read [the paper](../../report/report.pdf) for the physics, methods, results and derivations.
Read [the summary](model_test/summary.json) for all completed test measurements.
Both new selectors complete all 45 first attempts without fallback.
The original equation tree requires fallback in all 45 trials.
The seed and equation time ratios to native Kira are 1.0271 and 1.0171.
These results do not establish an overall time saving.
Native choices remain the application default for these cases.
The summary states the measured limits.
Do not assume that more training always reduces full calculation time.

## Data split

`cases.json` defines all propagators, scalar products, target indices and split assignments.
The study has nine training batches, six validation batches and nine test batches.
Training uses rational profiles 10 and 11 and the first four symbolic targets of each structure.
Validation uses rational profile 12 and symbolic targets 4 through 7, with indices starting at zero.
Testing uses rational profiles 13 and 14 and symbolic targets 8 through 11.
Each rational batch contains sixteen targets.
Each symbolic batch contains four targets.
Rational profiles use different momentum invariants in each split.
Symbolic target lists do not overlap within the symbolic split.
Rational cases reuse index templates at different parameter points.
All three structures occur in training and testing.
The test therefore measures adaptation within those structures.

The training label records membership in Kira's selected equation supports.
An equation support is its set of integrals with nonzero coefficients.
A seed has label one when at least one of its operators has a positive equation label.
These labels describe one useful native selection.
They do not prove that a seed or equation is necessary.

## Execution order

Run the scientific work on Hoffman through the scheduler.
Start in the project root.
Use the existing Python environment at `.tools/seed-model/venv/bin/python`.
It supplies NumPy, SymPy and Matplotlib.
The existing Kira binaries require the existing Fermat installation.

1. Submit `qsub ML_model_equation_selection/scattering_training/s01_job.sh all`.
2. Wait for `stage: complete` in the job log.
3. Submit `qsub ML_model_equation_selection/scattering_training/s04_analyze_job.sh`.
4. Read `model_test/summary.json` and check `all_exact`.

The first job saves each completed calculation before starting the next one.
A restart reuses these files and repeats unfinished calculations.
Keep the case definitions, model parameters and thresholds fixed during a reserved test.

## Code files

[s00_scattering_study.py](s00_scattering_study.py) defines the full study.
Its actions are `prepare`, `collect`, `train`, `validate`, `test`, and `all`.
`prepare` writes the case definitions and checks symbolic target separation.
`collect` obtains native reference reductions and labelled candidate equations.
`train` fits the six trees from training records only.
`validate` compares thresholds 0.001, 0.01 and 0.05 with three repetitions.
It selects each threshold from full validation time and writes `freeze.json`.
`test` uses five repetitions of native choices, the original equation tree and the two new trees.
It also checks applications without supplying target reference coefficients.

[s01_job.sh](s01_job.sh) submits this work with one CPU and explicit memory and time limits.
It accepts one action argument and defaults to `all`.

[s02_analyze.py](s02_analyze.py) checks all 180 reserved calculations and eighteen basis-only applications.
It reads saved results and never trains a model.
It writes test summaries and two paper figures.
The descriptive timing intervals resample three graph groups 10,000 times.
These intervals describe this small test and do not prove general performance.

[s03_reduce.py](s03_reduce.py) applies a fixed selector to a case from `cases.json`.
Its required options are `--case`, `--basis` and `--output`.
The basis file must contain a JSON list of master index vectors.
The output path must be inside this folder's `model_test` directory.
The optional `--policy` accepts `native`, `seed`, `equation` or `auto`.
The default is `native` because the reserved comparison gives no overall time saving.
The experimental automatic choice uses validation results only.
It requires no validation fallback and a time ratio below 0.98 before selecting a learned policy.
Otherwise, it uses native choices.
The application checks basis completion and retries with native equations when necessary.
The caller must use a scheduled job, as the reduction uses node temporary storage.

[s04_analyze_job.sh](s04_analyze_job.sh) runs the analysis with bounded resources.

## Inputs, outputs and limits

[references](references/README.md) stores native reductions from an enlarged seed region.
[training](training/README.md) stores native labels and their exact reference checks.
[validation](validation/README.md) stores threshold comparisons.
[trained_model](trained_model/README.md) stores the equation trees.
The [seed model folder](../../ML_model_seed_selection/scattering_training/README.md) stores the seed trees.
[model_test](model_test/README.md) stores all test runs and the summary.
[logs](logs/README.md) stores scheduler progress and completion records.
`freeze.json` records the settings and file checks fixed before testing.
`resource_plan.json` states the storage and memory budget.
`storage_audit.json` records the storage correction made during this study.

Keep new retained study files below 32 MiB across both model folders.
Run one scientific job at a time.
Each Kira attempt has a 150-second limit and a 32 MiB temporary-file limit.
The driver stops a process tree above its memory limit.
Project files, local report files and temporary files must remain below 10,000,000,000 bytes in total.
A Git download cache was reduced without removing working files or published history.
Avoid commands that download all historical data objects into the partial Git clone.

The earlier job was stopped during validation for this storage correction.
The replacement job reused completed records and repeated its unfinished calculation.
The reserved timing tests start after this correction.
Generated integral records and fitted model files stay on Hoffman and GitHub.
Only paper sources, figures and compact paper evidence tables are copied locally.
