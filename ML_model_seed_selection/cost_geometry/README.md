# Cost-trained sparse seed regions

This study reduces Kira work by selecting individual seeds before equation generation.
The first model learns the boundary of a sparse region from complete reduction times.
The second model predicts which fitted boundary gives the lowest cost for a requested target.
Kira generates the identities and performs exact algebra.
If a selected region fails, the program repeats the calculation without that restriction.
Every training and test cost includes these attempts and the final exact check.

The fitted domain contains planar and nonplanar two-loop boxes with rational kinematics and symbolic dimension.
Targets have unit positive physical powers and numerator ranks two through four.
Training, validation, and testing use separate kinematic profiles.
Some target index patterns recur across these splits.
The results do not establish a speedup at every loop order or for every integral family.

Use `s11_integrated.py` for the complete application.
It checks the exact massless-banana formula first.
It then uses the new seed policy in its validated domain.
Other inputs use the preceding Kira workflow.
Native calculations need a supplied master basis.

```bash
.tools/seed-model/venv/bin/python ML_model_seed_selection/cost_geometry/s11_integrated.py \
  --case case.json --basis basis.json --output result.json.gz
```

Run native calculations in a scheduled cluster job.
The bounded runner requires `JOB_ID` and `TMPDIR`.
The case file needs `id`, `size`, `definition`, and `targets`.
The definition contains loop and external momenta, propagators, physical propagator count, sectors, and kinematic rules.
The basis file contains a JSON list of integer index vectors.
Reference reduction coefficients are not application inputs.

The study uses Python 3.9, NumPy, and scikit-learn for training.
SymPy performs exact coefficient checks when coefficient strings differ.
Matplotlib draws the results, and the existing TeX build renders both documents.
The production predictor reads exported trees without importing scikit-learn.
The native executable is `.tools/kira-parametric/kira`.
See [the preparation guide](../../ML_model_adaptive_reduction/parametric_preparation/README.md) for its existing build procedure.
The native seed gate reads `KIRA_ML_SEEDS` before it constructs the IBP equations.
Its source is `Kira_comparison/acceleration/s03_seed_filter.h`.
The new study reuses this gate and executable.

The code sequence has separate training and test branches:

- `s00_policy.py` defines the seed regions, exact recovery, and storage limits.
- `s01_pilot.py` checks the seed interface on development inputs at two through four loops.
- `s02_job.sh` supplies one cluster core, bounded memory, and four hours of run time.
- `s03_train.py GRAPH` searches the seed-boundary parameters through complete native reductions.
- `s04_cost_model.py GRAPH` gathers more cost data and fits request-dependent cost predictors.
- `s05_reduce.py` compares native, fixed sparse, learned, and preceding application choices.
- `s06_test.py GRAPH` tests the frozen cost model with seven rotated repetitions.
- `s07_initial_test.py GRAPH` independently tests the first evolved boundary.
- `s08_analyze.py` computes matched times and paired repetition intervals.
- `s09_application.py` measures fresh processes with physical inputs and a master basis.
- `s10_document.py` writes the measured report section, derivation appendix, and timing plot.
- `s11_integrated.py` combines the new model with the preceding exact application.
- `s12_check_integration.py` checks model exports, input guards, and the complete public application.
- `s13_validation_worker.py` gathers independent validation cases on the third bounded worker.
- `s14_finish.py` checks the application, builds both documents, and audits their evidence.
- `s15_auxiliary_validation.py` gathers two further validation cases after the planar test worker finishes.
- `s16_parallel_test.py` runs three disjoint nonplanar test groups, then checks their completion.

The parallel test keeps every method and repetition for a request on one worker.
It preserves the original method order and exact checks.
Model parameters remain fixed before any reserved request runs.
Different requests can use different cluster workers.

`protocols/` defines the physical requests and their split.
`references/` contains unfiltered exact reductions and failed reference attempts.
`training/` and `validation/` contain the first search records.
`cost_training/` and `cost_validation/` contain the larger cost-prediction comparison.
`trained_model/` stores the fitted parameters and validation decisions.
`initial_test/` and `model_test/` contain the two independent comparisons.
`application/` measures process startup, loading, input, output, and checking.
Each timed record keeps its method, time, equation counts, recovery steps, and exact coefficients.
Failed attempts stay in the record.

The native control disables all learned decisions and retains tuned Kira seed bounds.
The fixed sparse control chooses one boundary per graph from validation data.
That control can use a boundary found during training, but it makes no cost prediction.
The previous control uses the preceding published application.
These controls separate sparse-region gains from the added gain of the cost predictor.
The combined resource limit is 10 GB across local files, Hoffman files, and node scratch.
The study limits retained files to 20 MiB and native scratch to 24 MiB per worker.
It runs at most three native workers at once.
The existing Kira executable enforces memory and time limits.
Data and trained models remain on Hoffman and GitHub.
The report, notes, and PDFs also have a local copy.


<!-- BEGIN MEASURED RESULTS -->
The first evolved seed boundary uses 22.3% less time than tuned native Kira on eight planar requests.
It uses 6.5% less time than the initial fixed-width control.
The broader selected workflow uses 22.2% less time than tuned native Kira on 20 matched two-loop requests.
It uses 22.6% less time than the preceding application.
Its comparison with the fixed sparse control gives 3.6% less time.
All successful outputs pass exact coefficient checks.
The fixed sparse control can use a boundary discovered during training.
See `summary.json` for intervals, individual times, failures, and scope.
double_box: Validation retains the fixed sparse boundary.
nonplanar_box: Validation enables the cost predictor.

<!-- END MEASURED RESULTS -->


<!-- BEGIN FINISH SCRIPT -->
Run `s14_finish.py` after both reserved test jobs and the validation helper finish.
It checks the application, writes both documents, and checks their evidence.
It does not publish files or change fitted models.
<!-- END FINISH SCRIPT -->
