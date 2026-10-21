# Exact vacuum reduction and trained seed choices

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

Use this folder for the combined exact and learned application.
The exact rule reduces a connected massless bubble tree with one massive vacuum root.
The cost model chooses a sparse seed boundary for supported native box targets.
The application retains the previous exact rules and native choices for other inputs.

Run from the project root on a compute node:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/vacuum_learning/s18_fast_runtime.py --case CASE.json --output ML_model_adaptive_reduction/vacuum_learning/requests/answer.json.gz --method integrated
```

Use the family definition and target-index format in protocol.json.gz.
The definition gives loop momenta, external momenta, propagators, masses, scalar-product rules, and physical propagator count.
Each target is an integer vector with one entry for each propagator, including auxiliary coordinates.
The result contains exact coefficients, master indices, completion status, and the selected native action when applicable.
Use --method all_fixed to disable the new model and select the fixed validation choice on eligible native inputs.
This control keeps the new exact vacuum rule.
Use --method previous to call the previous application.
The benchmark launches that application directly, so its timer does not include the new wrapper.

## Exact domain

The graph must form a connected rooted tree in the recognized momentum routing.
The root has one denominator with mass squared m2, or a positive rational mass squared.
All other physical lines are massless.
Every nonroot vertex has a self denominator and a difference with its parent momentum.
The root, edge, and leaf powers must be positive integers.
An internal massless self power can be zero or negative.
All auxiliary powers must be zero.
The implementation accepts one through thirteen loops and absolute powers at most sixteen.
It rejects cuts, symbolic index powers, other masses, and other physical graphs.
The paper derives the Gamma-product ratio to the unit-power master.
This rule gives an exact reduction within that domain.
It does not solve arbitrary massive vacuum or scattering integrals.

## Learned native domain

The eligibility gate requires two loops, three independent external momenta, nine integral indices, and zero propagator masses.
It checks these counts and powers rather than a graph name.
The measured native scope consists of planar and nonplanar boxes.
All seven physical powers are one, and the two auxiliary powers are nonpositive.
The numerator rank is one through four.
The interface accepts one through six targets and rational kinematics.
Training and the reserved comparison use one through four targets in planar and nonplanar boxes.
Inputs outside the training feature ranges use the fixed validation choice.
The policy has no topology-name input and does not predict reduction coefficients.
The three candidate seed boundaries share the exact checks, master basis, and native recovery.
The policy minimizes measured complete process time, with a cost penalty for an unverified outcome.
The batch sets of numerator-power pairs differ across training, validation, and reserved inputs.
Individual pairs can occur in different batches.
No reserved outcome enters fitting or selection.

## Files and order

- s00_vac_common.py loads the preceding application, defines model features, and bounds stored output.
- s01_vacuum.py recognizes the exact vacuum domain and computes rational coefficients.
- s02_native.py applies the new seed choice through the existing native reduction interface.
- s03_runtime.py is the first frozen application entry point.
- s04_cases.py defines complete vacuum coordinates and disjoint native target batches.
- s05_measure.py bounds fresh processes and prepares independent native references.
- s06_collect.py records training and validation times for each action.
- s07_job.sh runs one bounded scheduler job with one CPU thread.
- s08_train.py fits cost trees and selects the policy on validation data.
- s09_checks.py checks Gamma values, native coefficients, and rejected inputs.
- s10_prepare.py trains, checks the exact rule, and freezes the reserved protocol.
- s11_test.py runs one of two reserved workers and checks exact results.
- s12_analyze.py separates matched timing ratios from failures.
- s13_document.py writes the new results, derivation, plot, abstract, conclusion, and matching notes.
- s14_guides.py writes these guides and updates the main folder links.
- s15_validate.py checks the study and builds both documents.
- s16_finish.py analyzes both completed tests and builds the final documentation.
- s17_output_budget.py bounds transient output files under a process lock.
- s18_fast_runtime.py is the final complete application entry point.
- s19_fast_protocol.py freezes a separate request collection with unchanged model weights.
- s20_fast_test.py measures the final application and its controls on new requests.
- s21_fast_analyze.py separates the final application change from the model effect.

Run s06_collect.py 0 and s06_collect.py 1 first, in separate scheduler jobs.
Run s10_prepare.py after both collection jobs complete.
Run s11_test.py 0 and s11_test.py 1 only after the protocol exists.
Run s19_fast_protocol.py after both reserved workers complete.
Run s20_fast_test.py 0 and s20_fast_test.py 1 after the second protocol exists.
Run s16_finish.py after both final workers complete.
Preserve the existing evidence before repeating a study.
Use at most two native workers at once.

The scheduler sets one thread and a memory bound for each job.
Permanent study evidence has a four MiB allocation bound.
The final entry point uses a separate 512 KiB allowance for flat temporary request files.
This allowance comes from the existing per-application transient reserve.
Each compressed output must be below 256 KiB, and input and uncompressed output must be below three MiB.
A file lock protects the request budget when two workers write at once.
The application scans only the request directory for this check.
It does not scan permanent study data for each short analytic output.
The benchmark removes temporary request files before publication.
resource_plan.json records the combined project bound below ten GB.
Generated training data, model weights, and scientific outputs remain on Hoffman and GitHub.
Only the report and notes are synchronized to the local machine.

## Evidence and measured limits

model_application_audit.json counts failed internal attempts and generated equation instances in the final repetition.
It uses only native requests that both methods complete and verify in all repetitions.
It counts regenerated rows again and does not claim a count of unique IBP identities.

The vacuum rule completes 34/34 reserved requests; the preceding application completes 4/34.
The matched times are 5.045763 seconds for the preceding application and 0.729596 seconds for the new rule.
The new native model has time ratio 0.963420 against the fixed choice, with request interval [0.9365616433704154, 0.9838379126410454].
The model runs on 26 of 32 reserved native requests.
Each time is a sum of three-run request medians for matched completed requests.
Failures remain in the completion counts and receive no finite speed factor.
The timer includes startup, prediction, native recovery, exact application work, output, and exit.
Independent coefficient comparisons run outside both timers.
The native test uses two known topology classes. It does not establish transfer to arbitrary graphs.
The native 31-index restriction remains for unrecognized graphs.

The final entry point completes 22/22 separate requests. Its time ratio against the first revision is 0.964152, with request interval [0.9253984391158818, 0.997009563997195].
The unchanged model has ratio 0.963073 against fixed choices on 7 matched native requests, with interval [0.8985283361873264, 0.999238051179411]. The model completes all eight requests in every repetition; the fixed control completes 7 in every repetition.
The retained analytic rules have ratio 1.053402 against the preceding published entry point.
These separate collections do not provide speed factors that can be multiplied.
