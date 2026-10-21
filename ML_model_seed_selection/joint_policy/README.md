# Joint seed choices and exact scale reuse

This study trains models to select a seed boundary and Kira configuration from measured reduction costs.
Validation retains the preceding ML application for both graphs.
Neither new replacement clears the predefined 2% improvement threshold.
The retained application acts before Kira generates IBP equations.
Kira uses exact algebra and its native row choices.
An insufficient first attempt triggers the documented native recovery sequence.
All reported times include this repeated work.

The application can reuse an exact result after a common positive change of momentum scale.
It checks every dimensionless scalar-product ratio, the family, target indices, and master basis.
This rule applies to the two verified massless box definitions.
It uses only completed results from the current session.
The first request needs a reduction.
The cache stores at most 32 results and 1 MiB of serialized content in memory.
It writes no persistent result database.

## Application

Use `s05_application.py` from a scheduled Hoffman job at the project root.
The native runner requires `JOB_ID` and `TMPDIR`.

```bash
.tools/seed-model/venv/bin/python ML_model_seed_selection/joint_policy/s05_application.py \
  --case case.json --basis basis.json --output result.json.gz
```

The case file supplies `id`, `size`, `definition`, and `targets`.
The definition includes momenta, propagators, sectors, and scalar-product rules.
The basis file supplies a list of integer master-index vectors.
Reference coefficients are not application inputs.

Use a request list to share exact results within one process.
Each list entry has a `case` object and a `basis` list.

```bash
.tools/seed-model/venv/bin/python ML_model_seed_selection/joint_policy/s05_application.py \
  --requests requests.json --output results.json.gz
```

`--no-reuse` disables exact result reuse.
`--method native` disables all ML and uses tuned native seed bounds.
`--method fixed` loads one fixed configuration per graph and no model weights.
This fixed control applies within the fitted input domain.
`--method previous` uses the preceding complete application.
The default method is `learned`.
Unsupported model inputs retain the preceding analytic or native path.

The default request list measures first calculations and matching scaled requests together.
Its speedup depends on the presence of matching dimensionless kinematics.
The main model test disables result reuse.

## Inputs and training

The fitted inputs are planar and nonplanar massless two-loop boxes.
The targets have seven unit physical powers and numerator ranks two through four.
One or two auxiliary entries carry the numerator powers.
Kinematic values are rational, and dimension remains symbolic.
Every timed comparison supplies a master basis.

The development profile is 901.
Training uses profiles 911 and 912.
Validation uses profiles 921 and 922.
Reserved tests use profiles 931 and 932.
Some target index patterns recur across these divisions.
The results do not test new graph structures or all loop orders.

Development compares seed boundaries, integral orderings, and internal propagator-permutation settings.
Training fits measured complete log-time ratios for the retained configurations.
Models include regression trees, random forests, and extremely randomized trees.
Validation selects their depth, margin, and deployment condition.
The new model needs a 2% validation gain over the fixed control to use prediction.
Deployment also needs a 2% validation gain over the preceding application.
Frozen test results never change these decisions.

## Code order

1. Submit `s02_job.sh s01_pilot.py GRAPH` for each graph.
2. Submit `s02_job.sh s03_train.py GRAPH` after its pilot completes.
3. Submit `s02_job.sh s06_test.py GRAPH` after its model is frozen.
4. Submit `s02_job.sh s07_application_test.py GRAPH` after its reserved test completes.
5. Submit `s02_job.sh s12_compatibility.py` after a graph pipeline finishes.
6. Run `s10_finish.py` after all tests finish.
7. Review the rendered documents before publication.

Use `double_box` or `nonplanar_box` for `GRAPH`.
Keep at most three native jobs active at once.
The optional `s11_validation_worker.py` evaluates the second nonplanar validation profile in advance.
It preserves the candidate order and writes the same records consumed by the training job.
The nonplanar test uses two disjoint profile groups to reduce elapsed run time.
Set `JOINT_TEST_PARTS=2` and `JOINT_TEST_PART=0` or `1` for its two workers.
Each request keeps all methods and repetitions on one worker.
The original full-set worker remains in `protocols/s00_initial_test_worker.py`.
The nonplanar scale test also uses two disjoint groups.
Set `JOINT_APP_PARTS=2` and `JOINT_APP_PART=0` or `1` for its two workers.
All methods and repetitions for each base request stay on one worker.
The original scale worker remains in `protocols/s02_initial_application_worker.py`.
The original second-profile worker had no free memory for the later control job.
`s14_matched_validation.py` therefore repeats that profile with every control on one worker.
`s15_refit.py` preserves the original records and refits the model before any nonplanar reserved test.
The repeat protocol is in `validation_refit_protocol.json`.

`s00_engine.py` defines candidate reductions, physical inputs, exact checks, and bounded recovery.
`s01_pilot.py` compares configurations on development inputs.
`s02_job.sh` reserves one core and 8 GB of memory for one study stage.
`s03_train.py` fits predictors and freezes all validation choices.
`s04_reuse.py` checks scale equivalence and transforms exact coefficients.
`s05_application.py` supplies the complete application.
`s06_test.py` runs five rotated repetitions of four methods on reserved inputs.
`s07_application_test.py` tests fresh processes and exact scale reuse.
`s08_analyze.py` checks records and computes timing summaries and intervals.
`s09_document.py` writes both documents and the plot from saved results.
`s10_finish.py` checks guards, updates guides, builds both PDFs, and audits the evidence.
`s11_validation_worker.py` supplies the independent validation worker described above.
`s12_compatibility.py` checks existing four-loop native and eight-loop analytic paths.
The initial input reader expected an optional graph label on analytic inputs.
The corrected reader accepts those inputs, and all eight checks pass.
`protocols/s01_compatibility_initial.py` preserves the initial reader.
`s13_previous_validation.py` supplies the matched previous-application validation costs.
Its scheduler request was cancelled because the original worker had no free memory.
`s14_matched_validation.py` measures the complete replacement comparison on one worker.
`s15_refit.py` activates those costs and repeats the unchanged model search before testing.
`joint_policy_appendix.tex` gives the training definitions and scale-identity derivation.

## Data and dependencies

`protocols/` defines physical cases, candidate configurations, and data divisions.
`references/` holds independent native reductions used for exact comparison.
`pilot/`, `training/`, and `validation/` retain candidate timings and failed attempts.
`matched_validation/` holds the complete replacement comparison on one worker.
`validation_initial/` preserves the superseded comparison and preliminary model.
`trained_model/` holds fitted trees, fixed controls, and freeze records.
`model_test/` holds the reserved first-request reductions.
`application_test/` holds fresh-process scale sequences and their independent checks.
`compatibility_test/` checks the earlier paths outside the fitted graph domain.
`logs/` documents the scheduler output.
`summary.json` contains the measured aggregate and individual results.

The existing seed-model Python environment provides NumPy, scikit-learn, SymPy, and Matplotlib.
The application evaluates exported tree arrays without importing scikit-learn.
The native executable is `.tools/kira-parametric/kira`.
The existing [preparation guide](../../ML_model_adaptive_reduction/parametric_preparation/README.md) gives its build procedure.
The previous [seed study](../cost_geometry/README.md) documents the native seed gate and common runtime.

The study permits at most 20 MiB of retained files and 24 MiB of scratch for a new native attempt.
Reference discovery and earlier native paths permit 32 MiB per worker.
Three active workers therefore need at most 96 MiB of scratch together.
The common runner also enforces time, process memory, and file limits.
`resource_plan.json` bounds combined local, Hoffman, temporary, and publication storage below 10 GB.
Data and models remain on Hoffman and GitHub.
The paper, notes, and their rendered PDFs also have a local copy.

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
