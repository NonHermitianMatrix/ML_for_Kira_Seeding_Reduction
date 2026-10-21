# Exact formulas, reconstruction, and measured-cost selection

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

Use `s15_deploy.py` for this experiment.
It retains the preceding exact formulas, recurrences, and seed model.
It adds a separately built Kira 3.1 executable with FireFly 2.0.3 and FLINT.
The standard reconstruction algorithm supplies the algebra improvement.
A new cost model selects among six algebra settings only if validation admits it.
The current validation decision is `enabled=False`.

The comparison contains 22 fresh native requests and 53 analytic regression requests.
The integrated application completes 75 of 75 requests.
On 75 matched requests, summed median time changes from
79.624400 to 49.851771 seconds.
The ratio is 0.626087.
The added-model comparison against validated fixed settings gives ratio 1.008144.
The separate inherited-ML ablation gives ratio 0.982746 against its existing fixed procedure.
The cumulative comparison across the two latest extensions gives ratio 0.609235.
Read `summary.json` for intervals, failed attempts, slower requests, and individual times.
These results do not establish a fastest method for every integral.

## Run a request

Run the application on an allocated Intel Gold compute node with the documented modules.
The existing resource limits still apply.

```bash
module load gcc/9.5.0 python/3.9.6 gmp/6.2.1 flint/2.8.0
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/reconstruction_policy/s15_deploy.py --case /absolute/request.json --output ML_model_adaptive_reduction/reconstruction_policy/requests/result.json --method integrated
```

The case schema is the existing complete physical request schema.
It includes propagator momenta, squared masses, scalar products, and target indices.
Use `s10_cases.py` and `test_protocol.json.gz` for concrete input definitions.
Scientific request data remain on Hoffman and GitHub.
The application checks the processor before using the verified reconstruction build.
Other processors retain the preceding application.
Loop orders outside the new native training range also retain that dispatch.
The exact formulas still cover their specified domains through thirteen loops.

`integrated` uses the admitted configuration.
`fixed` uses the validated setting for each propagator structure without loading new model weights.
`previous` calls the preceding direct analytic application.
`before_formulas` calls its predecessor.
The last control measures the cumulative change across these two extensions.
It is not unmodified Kira.
Both new controls retain the preceding seed model.
Learned row selection and the separate equation filter remain off.

## Data and model

The input generator defines 48 training, 22 validation, and 22 reserved native requests.
There are four propagator structures at two and three loops.
Whole physical requests are disjoint between splits.
Some target indices and all four graph structures recur.
The kinematic numbers are rational; the dimension remains symbolic.
This is not general symbolic scattering kinematics.

The six actions are preceding symbolic reduction and FireFly with batch sizes 1, 2, 4, 8, and 16.
These are probe batch sizes, not target counts.
The model uses 29 mathematical input features.
It predicts relative complete cost and observed failure fraction.
Training measures one complete application per action; validation measures three.
Each candidate has 32 extremely randomized trees.
Validation selects depth, leaf size, and saving margin.
Deployment requires at least three percent less validation cost and no failed selected attempt.
The fixed control separately selects its setting for each propagator structure.
Inputs outside the training feature ranges use the preceding application.
Failed reconstruction retains its cost and invokes symbolic recovery.
A failure score cannot guarantee completion.

The model was fitted from 48 training requests and 22 validation requests.
Read `training_summary.json` for all candidate settings and the deployment decision.
Read `trained_model/README.md` for saved weights and configurations.
`entry_checks.json` compares the exported predictor with the fitted estimator.
It also checks complete applications before the reserved test.
`training_source/` preserves the exact fitting script.
The current script changes only the numerical tolerance in its feature-consistency audit.
The exported predictions agree with the fitted estimator within 1e-12.

## Build and reproduction

The separate binary is `.tools/kira-reconstruction/kira`.
The preceding binary remains `.tools/kira-sector-wide/kira`.
The build uses the published patched Kira sources and a pinned compatible FireFly revision.
`dependency.json` records that upstream source and archive digest.
`gmp_cpp_dependency.json` records the official matching GMP 6.2.1 header.
The cluster supplies GMP and FLINT.
The system C++ stream library supplies GMP stream operations.
The compiled FireFly objects use the C++ ABI of the preceding Kira build.
`build.json` contains every compilation and link command, source digest, and module version.
Tool binaries and compilation objects are not published to Git.
The Git repository contains the reproduction records and research data.

Run `s01_fetch_firefly.py`, then `s09_fetch_gmp_header.py`.
Submit `s03_build.sh` to build with two compiler workers.
Do not run native tests during the build.
Submit the development wrappers only after the build succeeds.
Submit `s22_learn.sh` to collect the training and validation costs and fit the model.
Submit `s25_model_test.sh` after training finishes.
It checks the entry point, freezes the protocol, and runs two bounded test workers.
Prepare the inherited-ML ablation with `s34_retained_test.py prepare`.
Submit `s35_retained_test.sh` after the main test.
It uses the same reserved inputs and fixed algebra settings, without fitting a new model.
Run `s36_analyze_retained.py` after both workers finish.
Then run `s26_analyze.py`, `s27_plot.py`, `s29_write_results.py`,
`s28_write_paper.py`, `s31_write_guides.py`, and `s32_validate.py`.
The numbering records script development; this paragraph specifies the final execution order.

## Script guide

- `s00_reconstruction_common.py` defines paths, bounded storage, unique module loading, and atomic records.
- `s01_fetch_firefly.py` fetches the pinned compatible source and verifies its archive.
- `s02_build.py` builds the separate native executable and removes its new temporary objects.
- `s03_build.sh` allocates a bounded build job on an Intel Gold node.
- `s04_native.py` changes native algebra options while preserving the bounded runner and basis checks.
- `s05_runtime.py` exposes the experimental algebra actions through the preceding exact application.
- `s06_measure.py` measures a complete fresh process, including failure and cleanup.
- `s07_pilot.py` compares the initial four development requests.
- `s08_pilot.sh` submits that development comparison.
- `s09_fetch_gmp_header.py` fetches the matching official C++ header and licenses.
- `s10_cases.py` defines the separate physical requests and features.
- `s11_collect.py` measures training or validation actions against symbolic coefficients.
- `s12_collect.sh` provides the two-worker collection wrapper.
- `s13_cost_decision.py` evaluates the compact exported forest and applies its admission rules.
- `s14_train.py` fits candidate models and selects them with validation only.
- `s15_deploy.py` provides the retained complete application with bounded symbolic recovery.
- `s16_bunch_pilot.py` tests probe batch sizes and simple box requests.
- `s17_bunch_pilot.sh` submits that pilot.
- `s18_structure_pilot.py` adds massive sunrise and three-loop vacuum development requests.
- `s19_structure_pilot.sh` submits that pilot.
- `s20_reference.py` prepares separate symbolic reference coefficients in the protected basis.
- `s21_prepare_learning.py` checks split separation and massless external kinematics.
- `s22_learn.sh` collects the two splits and fits the model.
- `s23_prepare_test.py` freezes inputs, code, weights, and executable records before the final test.
- `s24_model_test.py` compares four applications on its assigned frozen requests.
- `s25_model_test.sh` checks the entry point and submits the paired final comparison.
- `s26_analyze.py` computes paired ratios, completion counts, uncertainty, and the separate ML effect.
- `s27_plot.py` draws the four report figures from the saved results.
- `s28_write_paper.py` updates the methods and preserves the earlier evidence in the notes.
- `s29_write_results.py` writes the measured results and physical input appendix.
- `s30_check_model.py` checks prediction export and complete development applications.
- `s31_write_guides.py` updates this guide, folder guides, and current entry pointers.
- `s32_validate.py` checks frozen evidence, preserved methods, documents, and resource bounds.
- `s33_retained_ml.py` switches inherited learned choices off while sharing the validated algebra setting.
- `s34_retained_test.py` freezes and measures that separate paired ablation.
- `s35_retained_test.sh` runs its two bounded workers after the main comparison.
- `s36_analyze_retained.py` reports its elapsed time, completion, and recorded seed sequences.

## Exact checks and interrupted trials

Every final coefficient is compared with a separate exact reference.
For native reconstruction, that reference is a symbolic Kira calculation.
Some larger complete-region confirmations exceeded the reference bound.
The published symbolic application still supplies their independent symbolic coefficients.
`expanded_reference_attempt/`, `ordering_reference_attempt/`, and
`complete_region_reference_attempt/` preserve those preparation trials.
They do not represent failed model-selected applications.

`kinematic_convention_attempt/` preserves an early nonplanar input error.
Its scalar-product signs did not match the intended outgoing-momentum convention.
Those records were removed from training before model fitting.
`kinematic_checks.json` verifies the corrected on-shell conditions and invariant metadata.
`pilot_basis_checks.json` resolves two pilot comparisons made in different master bases.
The original pilot output remains preserved.
No reserved outcomes select the model or its settings.

## Resource bounds

The combined project ceiling is 10,000,000,000 bytes.
The conservative preceding persistent bound is 9,778,738,176 bytes.
Retained new tools use at most 32 MiB; study files use at most 20 MiB.
Stage files and logs reserve 4 MiB.
Two native workers reserve 96 MiB for scratch and transient application files.
Publication reserves 140 MiB for report copies, Git, and temporary document files.
Native tests stop before publication.
The larger bound is 9,984,259,072 bytes; `resource_plan.json` gives the exact computed value.
Each native calculation uses one computational thread.
The wrappers limit address space and output files.
Keep other user jobs unchanged.

Use `s15_deploy.py` for one request. Use `s37_batch.py` for a bounded collection of 1 to 128 requests. The shared call retains loaded routines and policies. It receives no reference answers and computes each requested reduction.

From the project root, run:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/reconstruction_policy/s37_batch.py --cases /path/to/cases.json --output /path/to/new-results.jsonl
```

The input is a JSON list of request objects in the existing application format. Each request needs a distinct `id`. The input must be smaller than 2 MiB. The output path must not exist. Each output line contains `case`, `result`, and the internal request time `seconds`. Read `result.success` for each request. A caught request exception produces a failed result and the next request runs. Native attempt limits remain active. An outer process failure can leave a partial file; check that every input ID has a result. The output is limited to 8 MiB and each line to 2 MiB. Use compute nodes and the same one-thread settings as the test script.

The optional `--method` selects `integrated`, `fixed`, `previous`, or `before_formulas`. The default is `integrated`. These choices match the single-request application. A collection call does not create a new learned model.

The frozen comparison uses the same 75 verified requests, four methods, and three repetitions. It reverses request order in the middle repetition and checks every coefficient against the saved independent references. It is an implementation regression test, not a new held-out physics sample. Current separate calls take 58.980439 s at the median; the shared call takes 37.246748 s. The earlier shared call takes 70.050574 s. All 900 executions pass 18132 coefficient checks. No reconstruction choices change.

`s38_prepare_batch.py` freezes the inputs, code, weights, binary, and references. `s39_batch_test.py` times and verifies the applications. `s40_batch_test.sh` submits two bounded workers. `s41_analyze_batch.py` computes the summaries. `s42_write_batch.py` updates the documents and guides. `s43_validate_batch.py` verifies the final files. Read `batch_protocol.json.gz`, `batch_summary.json`, and `batch_resource_plan.json` for the protocol, complete results, and storage bounds. The `batch_test` folder contains all timed outputs. Training and all earlier experiments remain unchanged.
