# Training for scattering integrals

This study uses training examples from three scattering structures.
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

## Scripts

| File | Purpose |
|---|---|
| [s00_scattering_study.py](s00_scattering_study.py) | Train native seed and equation trees on three previously unsupported families. |
| [s01_job.sh](s01_job.sh) | Scheduler wrapper for job; its header sets the resource limits. |
| [s02_analyze.py](s02_analyze.py) | Check all reserved runs and make the scattering results table and figure. |
| [s03_reduce.py](s03_reduce.py) | Apply a frozen scattering selector with a supplied master basis. |
| [s04_analyze_job.sh](s04_analyze_job.sh) | Scheduler wrapper for analyze job; its header sets the resource limits. |
