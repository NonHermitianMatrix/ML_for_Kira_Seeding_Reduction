# Direct analytic evaluation and native seed selection

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

The final entry point is s23_deploy.py.
If a replacement model fails validation, the final application retains the preceding native ML policy.
It first returns zero for homogeneous massless vacuum families.
It uses exact partial fractions for supported vacuum factors.
It returns explicit Gamma-function values for their tadpoles.
It also returns the analytic master value for supported connected one-mass vacuum trees.
Other accepted exact rules remain available through the preceding application.
For supported native boxes, validation selects whether to use a cost model or a fixed seed procedure.
The candidate procedures use a tight sparse, wide sparse, or complete seed region.
The model does not predict physical coefficients.

The rejected replacement model has 24 training batches and 12 validation batches.
The retained native model has 34 training batches and 16 validation batches.
A separate final test has 16 fresh native batches. Whole batches do not cross these splits.
The same planar and nonplanar graphs occur in each split. Individual targets can recur.
The final comparison has 69 requests. A further 26 requests test repeated-mass factors and coupled massless vacuum families.
Vacuum products and connected trees cover each loop order from 1 through 13.
This does not cover all coupled high-loop scattering integrals.

The integrated method completes 69 of 69 main requests.
The preceding method completes 69.
Their 69 matched requests take 109.273070 and 111.949525 seconds.
The separate integrated/fixed native ratio is 1.001865.
Validation disables the replacement learned choice.
The final deployment retains the model in lightlike_reduction/trained_model when this replacement is disabled.
Read final_summary.json for current uncertainty, slower cases, and failures.
Read summary.json for the rejected replacement comparison.

## Run

Run on a Hoffman compute node in the project environment.
Use the existing family definition and target format.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/direct_analytic/s23_deploy.py --case request.json --output ML_model_adaptive_reduction/direct_analytic/requests/result.json --method integrated
```

The output path must stay in this study folder. The writer limits study records to 12 MiB.
Use `fixed` to disable the retained learned native choice.
Use `previous` to run the preceding published application.
The explicit actions are `order1` for tight sparse seeds, `wide` for wide sparse seeds, and `dense` for all seeds in the tight procedure's finite outer bounds.
The dense action retains the same exact basis check and recovery.
The ordering pilot also accepts `order2` through `order8`; these are not deployed choices.
Native output remains an exact master decomposition.
For accepted vacuum cases, `master_values` also gives the analytic value.
Gamma argument pairs [a,b] mean a+b*d/2. Dimensional poles remain in these values.

## Reproduce

1. Submit `s06_pilot.sh` for the separate ordering pilot.
2. Submit `s13_train.sh` after the pilot finishes. It selects the action set, checks the exact formulas, measures each training and validation action twice, and trains the model.
3. Submit `s22_test.sh` after training finishes for the candidate comparison and exact-domain coverage.
4. Submit `s34_deploy.sh` after that job ends. It freezes the final deployment and fresh whole target batches, runs two workers, and writes the current paper and notes.

Keep frozen source and model files unchanged during testing.
The application limit is 30 seconds. Each test has three repetitions.
Method order rotates on the same worker. There is one computational thread per application.
External references and their final coefficient comparison are outside the application timer.
Native applications use protected master indices. They do not use reference coefficients to choose an action.
All failed application costs remain in the records.
Training gives an unverified action a cost of at least 60 seconds.

## File sequence

- s00_direct_common.py: shared paths, lazy imports, and bounded records.
- s01_runtime.py: exact dispatch, explicit values, learned choices, and native integration.
- s02_measure.py: full process timer and bounded termination.
- s03_cases.py: disjoint native input batches.
- s04_pilot.py: all eight integral orderings on development inputs.
- s05_vacuum.py: scaleless recognition, exact partial fractions, and tadpole recurrence.
- s06_pilot.sh: two-worker pilot allocation.
- s07_exact_cases.py: exact physical grids through 13 loops.
- s08_checks.py: independent algebra, quadrature, and native checks.
- s09_select_actions.py: retain the ordering result and define the final actions.
- s10_collect.py: complete training and validation costs.
- s11_failure_guard.py: empirical action-failure models and feature-range checks.
- s12_train.py: cost-tree fitting, validation, and deployment condition.
- s13_train.sh: bounded collection and training allocation.
- s14_prepare.py: frozen model, sources, cases, and test limits.
- s15_test.py: complete held-out comparison and exact checks.
- s16_analyze.py: completion counts, paired ratios, and uncertainty.
- s17_plot.py: loop-by-loop times and the separate learned effect.
- s18_document.py: current paper, notes, and derived equations.
- s19_guides.py: this guide and the folder guides.
- s20_validate.py: frozen evidence, analytic values, documents, and storage checks.
- s21_finish.py: analysis, documents, guides, and validation.
- s22_test.sh: bounded test and publication-preparation allocation.
- s23_deploy.py: preserve the preceding native model when the replacement fails validation.
- s24_deployment_cases.py: fresh final targets and native kinematic point.
- s25_deploy_measure.py: complete-process timer for the final entry point.
- s26_deploy_prepare.py: freeze final sources, retained weights, and requests.
- s27_deploy_test.py: final complete-time comparison.
- s28_deploy_analyze.py: final totals and separate retained-ML comparison.
- s29_deploy_check.py: final source and model checks.
- s30_deploy_plot.py: figures for the final held-out results.
- s31_deploy_document.py: final paper and notes entry point.
- s32_deploy_validate.py: final mathematical, document, and resource checks.
- s33_deploy_finish.py: final analysis and documentation sequence.
- s34_deploy.sh: bounded final scheduler allocation.
- s35_import_check.py: check all three native controls after the import-name correction.
- focused_main.tex: candidate paper template.
- focused_final_main.tex: current paper template.
- focused_derivations.tex: exactness, native seed definitions, and cost objective.
- direct_appendix.tex: partial-fraction and analytic-value derivations.
- protocol.json.gz: frozen requests and source identities.
- summary.json: original candidate result summary.
- final_protocol.json.gz: frozen final requests, sources, and retained model identity.
- final_summary.json: current final result summary.
- validation.json: completed checks and PDF identities.
- resource_plan.json: combined local and remote storage bound.

## Limits

The scaleless rule accepts homogeneous massless vacuum families through 13 loops and 128 coordinates.
It permits coupled loop momenta, but excludes cuts and symbolic indices.
The new partial-fraction rule accepts independent loop directions without external momenta.
Each component can have at most eight denominators. Each index has absolute value at most eight.
Equal masses combine before expansion. The resulting total positive power is at most 48 per component.
Masses are nonnegative rational numbers. The accepted products have at most 13 loops.
Connected trees use their separate one-mass rule and its stated power bounds.
Unsupported inputs retain the preceding exact and native procedures.
A classifier score does not prove success for an unseen integral.

Keep at most two native workers active. Each has one computational thread and 32 MiB of native scratch.
The scheduler wrappers allow 8 GiB per slot; child processes retain their smaller limits.
The combined project limit is 10,000,000,000 bytes, including both machines, Git, and temporary files.
Generated scientific data stay on Hoffman and GitHub. The laptop receives the report folder.
Earlier source, model, and result files remain unchanged.
