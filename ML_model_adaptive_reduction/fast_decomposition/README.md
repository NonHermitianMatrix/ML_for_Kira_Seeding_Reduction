# Fast exact decomposition with learned decisions

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

This folder contains the next application after analytic_decomposition.
It uses exact formulas for supported integral families.
It splits independent loop blocks before reduction.
A trained tree can select a recurrence strategy. Complete-cost validation currently keeps the fixed recurrence strategy.
The retained seed model selects Kira settings for its validated coupled blocks.
Other inputs use the preceding exact and native reduction methods.

## Run order

Run each scientific step on a scheduled compute node with s05_job.sh.
Keep at most two native workers active.

1. Run s04_pilot.py to check the formulas and recurrence strategies.
2. Run s06_train.py to collect training costs and select the recurrence model.
3. Run s07_cases.py to freeze the sources, models, and reserved inputs.
4. Run s08_test.py 0 and s08_test.py 1 to test the two disjoint request lists.
5. Run s09_analyze.py after both workers finish.
6. Run s10_document.py and s11_validate.py to update and check the documents.

The first pilot failed during an import, before any calculation.
Unique module names fixed this error. The second pilot passed.
These pilot inputs do not enter the reserved timing results.

## Code

s00_fast_common.py supplies input normalization, block splitting, basis checks, and bounded file writes.
s01_fast_recurrence.py applies the scalar one-loop IBP recurrence with exact rational arithmetic.
s02_fast_formulas.py evaluates finite products for the supported analytic families.
s03_fast_runtime.py preserves the initial candidate and combines these stages with the learned and native Kira methods.
s04_pilot.py compares the new coefficients with earlier independent formulas or recurrence results.
s05_job.sh sets the resource limits and starts a scheduled calculation.
s06_train.py records recurrence costs and fits the decision tree.
s07_cases.py defines the reserved requests and freezes the protocol.
s08_test.py records full process times, exact checks, failures, and the coverage audit.

Use this command inside a scheduled job:

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/fast_decomposition/s12_deploy.py --case CASE.json --output ML_model_adaptive_reduction/fast_decomposition/requests/RESULT.json.gz --method final
```

For the initial candidate only, use s03_fast_runtime.py with --method fixed to disable both learned decisions. The final entry point uses the modes listed below.
Use the actual prior application for the previous and native controls, as shown in s08_test.py.
Each timing starts a fresh process and includes the exact output comparison.
Master discovery and reference preparation remain separate.
The prepared basis contains master indices. It contains no answer coefficients.

## Mathematical scope

The new finite products support massive tadpoles, one-mass vacuum bananas, and massless propagator bananas.
The banana formulas support positive physical indices and at most one auxiliary quadratic numerator with power minus one.
The auxiliary denominator must have zero mass.
Scaleless vacuum integrals vanish in dimensional regularization.
The one-loop recurrence supports at most five scalar denominators and six extra positive powers.
It requires rational kinematics and invertible sector matrices.
An unsupported recurrence returns the request to the previous application.
Independent blocks extend these methods to some products with many loops.
These products do not establish general connected high-loop scattering coverage.

The audit includes vacuum, two-point, and scattering families at every loop count through thirteen.
It records native input limits, incomplete reductions, and timeouts.
A finite grid cannot contain every integral family or every choice of indices and kinematics.
Read the completed summary for the actual supported cases and failures.

## Training and controls

The new model chooses among largest-power, smallest-power, first-index, and last-index recurrence strategies.
It uses eleven features from the target powers and batch size.
Training uses 112 requests at two kinematic profiles.
Validation uses 56 requests at a third profile.
Each strategy runs three times per request. The median kernel time supplies its cost label.
Every strategy must give the same exact coefficients.
Validation selects a tree, a prediction margin, and one fixed strategy.
The model needs at least a two percent validation saving before it is enabled.
Reserved full-process tests measure whether this kernel saving helps the complete application.
The prior sparse-seed model retains its original weights.

The four timing methods are learned, fixed, previous, and native.
The fixed method uses the same fast exact code with fixed choices.
The previous method runs the preceding deployed application without changes.
The native control retains the prior exact formulas and uses native Kira choices for the remaining work.
Thus the native control is already accelerated. It is not stock Kira on every target.

The separate coverage audit gives each application a twenty-second limit.
Its results measure bounded completion, not a final impossibility of reduction.
The timing comparison uses a 125-second outer limit and three rotated repetitions.
Failed requests remain in the summary and receive no completed-time speedup.

## Resources and dependencies

Each worker uses one core and at most 8 GiB of scheduled memory.
Native calls have additional memory, time, and scratch limits.
The persistent study cap is 12 MiB. Read resource_plan.json for the combined project bound.
Keep scientific data and model files on Hoffman and GitHub.
Only document artifacts and source staging belong in the local workspace.

The exact recurrence uses gmpy2 2.2.1 from .tools/fast-arithmetic.
This isolated install leaves the shared Python environment unchanged.
Set SYMPY_GROUND_TYPES=python for every control and candidate measurement.
This keeps the old symbolic arithmetic backend the same across methods.
The runtime imports the larger legacy application only when a block needs it.

Optional upstream Torch C++ headers and downloaded source archives were removed to recover storage.
The runtime libraries, installed tools, model weights, and Git history remain available.
Reinstall the same Torch package if a future task needs to compile a Torch extension.
The obsolete compressed migration index matched its saved Git tree before removal.
The saved commit and migration logs remain available.
Identical protoc executable names now refer to the same file content through a hard link.

## Completed reserved comparison

The new application verifies 65 of 65 requests in all three repetitions.
The separate audit completes 68 of 110 requests within twenty seconds each.
all, previous control: 65 matched requests; time ratio 0.698070; repetition interval [0.6755947836016626, 0.7166531678502016].
all, native control: 65 matched requests; time ratio 0.348570; repetition interval [0.33810971928444583, 0.35953494159570554].
all, fixed control: 65 matched requests; time ratio 0.956967; repetition interval [0.9252212925032454, 0.9864451011577298].
recurrence, previous control: 9 matched requests; time ratio 0.313569; repetition interval [0.30442669195371497, 0.32869799921571347].
recurrence, native control: 9 matched requests; time ratio 0.179539; repetition interval [0.17242046678290004, 0.18981346466666113].
recurrence, fixed control: 9 matched requests; time ratio 1.002272; repetition interval [0.9594551248312766, 1.0763609882073937].
learned_native, previous control: 8 matched requests; time ratio 1.016346; repetition interval [0.9778290174433023, 1.0502715472699338].
learned_native, native control: 8 matched requests; time ratio 0.593355; repetition interval [0.5589876260302296, 0.6142725277319153].
learned_native, fixed control: 8 matched requests; time ratio 0.932212; repetition interval [0.8879269616909006, 0.9607058351084723].

Read summary.json for every timing, failure count, and audit outcome.
Read validation.json for the frozen-evidence and document checks.
The report separates exact implementation savings from learned gains.
## Final complete-cost deployment

The final entry point is s12_deploy.py.
Use --method final for the deployed workflow.
Use --method candidate to enable the recurrence tree, or --method fixed_recurrence to disable that tree only.
The native seed model remains active in both alternatives.
s13_application_gate.py tests full application cost on the original 56 validation requests.
s14_deployment_test.py freezes the decision and tests twelve fresh requests.
s15_deployment_document.py checks these results and writes the final report section.
The recurrence tree is disabled by full-cost validation. Its validation time ratio is 0.990587.
The separate final test has a ratio of 0.639807 to the preceding application.
The initial 65-request experiment and 110-request audit remain unchanged.
Read deployment/summary.json for the separate final test.
After s06_train.py, run s13_application_gate.py on the validation split. Run s14_deployment_test.py after admission.json exists and both audit workers finish. Run s11_validate.py last.
s16_resume_audit.py resumes the unchanged audit after an older result omitted an optional status label. It reuses all recorded times.
The independent validation reference limit increased from ten to 120 seconds after one slow Fraction-arithmetic reference. Completed application times remain unchanged.

initial_document_validation.json retains the first document check. validation.json identifies the final paper and notes.
To install the isolated rational-arithmetic dependency, run this command from the project root:

```sh
.tools/seed-model/venv/bin/python -m pip install --target .tools/fast-arithmetic --no-cache-dir --no-compile --no-deps --only-binary=:all: gmpy2==2.2.1
```
