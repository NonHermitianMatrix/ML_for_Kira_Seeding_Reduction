# Learned batch equation reuse

This extension reduces supplied Euler and partial-fraction systems of the restricted coupled vacuum family. It supports two to four distinct massive denominators, total massive power at most fourteen, unit massless powers and any positive loop order (at most 32 loop orders in one request). Tests cover loops one through twelve and separate exact applications at 16, 24 and 32. General native high-loop IBP generation remains outside this domain.

The model predicts a weighted equation count for each fixed mass ordering. Its choice supplies a terminating dependency closure, including the actual Euler seeds. Kira performs exact elimination. A polynomial reference checks coefficients before exact substitution to each loop order. Grouped requests retain distinct master bases for their mass profiles.

Training uses 420 batches and 6,300 candidate orderings. Validation selects forest4.json, with 7634 nodes. Scores predict log cost and are not confidence probabilities. Original JSON trees, lossless compact weights, generated C inference and shared libraries remain in trained_model/. Compiled and Python scores match for 12,600 checked candidates.

## Deployment and results

Single-profile default: extreme. Final grouped default: python backend with forest4.json; control: extreme. Validation requires a 2% complete-time improvement for learned deployment.

There are 300 first reserved calculations, 80 grouped comparisons and 80 fresh backend comparisons. All pass exact checks without fallback. Seven further normal integration applications pass; one injected check failure verifies the full-system fallback. The selected final complete-time ratio to the preceding separate workflow is 0.220, with descriptive interval [0.17092620490860583, 0.27025241334125893]. The compiled learned ratio to the updated grouped control is 0.923. Mean weighted-cost regret against enumerated mass orders is 1.035.

Savings include separate contributions from equation sharing, exact verification in z, integer polynomial arithmetic and sharing Kira calls. A direct analytic solution exists for this restricted family. These tests do not establish a globally fastest reduction.

## Usage on Hoffman

Use bounded scheduler jobs. A single-profile request has the format documented in ../higher_loops/README.md:

~~~bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s09_application.py --input request.json --output ML_model_equation_selection/batch_reuse/model_test/application.json
~~~

For grouped use, put single-profile requests in an object with a requests list. Limits are eight profiles, 512 targets and 12,000 selected equations.

~~~bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s17_application.py --input group.json --output ML_model_equation_selection/batch_reuse/model_test/group_application.json
~~~

Explicit backends are native, python and control. The previous backend runs the preceding separate workflow. Rebuild platform-specific libraries with s16_native.py when required. The earlier s11_pack.py interface preserves the first packed deployment.

Result JSON files reference SHA-256-checked compressed objects containing source choices, raw Kira exports, logs and exact rational coefficients as numerator/denominator pairs. Symbolic coefficients use z; expanded coefficients use d and are grouped by loop order and profile. Failed combined systems retry profiles separately; failed selected systems retry the full supplied pool.

## Reproduction

Run s01_train.py, then s04_run.sh validation. Use s13_run.sh for validation selection, packed validation, freezing and reserved tests. Use s19_run.sh for integration checks, identical compiled inference and fresh backend validation/testing. Finish with the audit, plot, document and release-check scripts. Completed experiment records are preserved. development_initial/ contains the original pilot code.

- s00_common.py: Batch equation choices for the restricted, exact vacuum coefficient system.
- s01_train.py: Train a fast predictor of shared equation-substitution cost.
- s02_reduce.py: Kira integration with learned batch choices and shared exact checks.
- s03_study.py: Sequential paired fresh-case evaluation, with all calculation costs counted.
- s04_run.sh: Bounded scheduler wrapper.
- s05_check.py: Independent arithmetic and domain checks, including equivalent loop expansions.
- s06_select.py: Select only on validation complete costs, then freeze before fresh tests.
- s07_compact.py: Store exactly the same trained trees in a bounded compact representation.
- s08_reader.py: Fast exact integer-polynomial reader with the previous rational reader as fallback.
- s09_application.py: Public entry point for the frozen, validated batch reduction deployment.
- s10_analyze.py: Fresh-case complete times and independent exact audits of saved reductions.
- s11_pack.py: Reduce several independent mass profiles in one exact Kira system.
- s12_pack_study.py: Paired packed/separate applications, preserving identical targets and checks.
- s13_run.sh: Bounded scheduler wrapper.
- s14_pack_analyze.py: Audit every saved packed result against the independent original loop oracle.
- s15_integration.py: Check production entry points, extended loop values and exact fallback.
- s16_native.py: Compile unchanged trained trees and compare all scores exactly.
- s17_application.py: Apply identical learned choices through a native inference library.
- s18_native_study.py: Fresh native-inference validation followed by frozen independent confirmation.
- s19_run.sh: Bounded scheduler wrapper.
- s20_native_analyze.py: Audit native-backend confirmation and compare full applications.
- s21_plot.py: Reproducible figures of complete exact application times.
- s22_document.py: Write report and READMEs from audited complete calculation results.
- s23_release_check.py: Release guards for exactness, unchanged earlier studies and the storage ceiling.
- s24_native_application_check.py: Check the final public deployment and compiled backend at extended loop orders.

## Resource accounting

Only one experiment job runs at a time. Each Kira attempt has a 90-second limit, a 1,800 MiB address-space limit, a 1,500 MiB sampled process-tree RSS guard and a 64 MiB scratch guard. The job has separate memory limits. resource_plan.json bounds combined local and cluster storage below 10,000,000,000 bytes. Scientific data stay on Hoffman and GitHub; only report material is copied locally.
