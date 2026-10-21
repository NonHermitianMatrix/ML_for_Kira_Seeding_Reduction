# Exact massless banana reduction

This directory contains a component or comparison experiment. The [combined application](../triangle_reduction/README.md) selects the retained methods.

This study implements an exact formula for a defined massless two-point family.
At L loops, the family has L loop denominators and one denominator for their sum minus the external momentum.
All physical powers must be positive integers. Auxiliary powers must be zero.
The external squared momentum must be nonzero.
The formula reduces each allowed target to the corner integral with all physical powers equal to one.
We measure this analytic saving separately from the contribution of the models.

## Current evidence

The first native test retains eight failed higher-loop requests.
The follow-up selects fixed seed bounds on a separate development point.
It completes 9 matched requests and leaves 1 without a completed comparison.
No six-loop development choice passes the memory limit, so its reserved request does not run.
All successful native coefficients agree exactly with the formula.
There are 240 independent high-precision Gamma-function checks.
These checks cover loops 1 through 12, 16, 24, and 32.
The proof applies to every positive loop count under the stated assumptions.
The implementation limits the loop count to 64 and total extra powers to 256.
General scattering families do not satisfy this formula.

## Use the combined interface

Run from the project root on a Hoffman compute node.
Supply a JSON case with `id`, `size`, `targets`, and `definition`.
Native run labels are optional. The adapter identifies known graphs from their physical definitions.
The definition gives the momenta, propagators, masses, scalar products, and invariants.
It also gives `physical_propagators` and `top_level_sectors`.
The case examples are in `model_test/protocol.json` and `application/protocol.json`.

```sh
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/massless_banana/s03_route.py --case CASE.json --basis BASIS.json --output RESULT.json.gz --strategy learned
```

The interface checks the analytic domain first.
An accepted request uses exact rational products and needs no model import.
Other requests use [the native batch workflow](../batch_policy/README.md).
It loads the compact frozen policy and omits unused tree arrays when the batch predictor is disabled.
That workflow requires a supplied master basis and accepts at most 31 integral indices.
The basis file contains a JSON list of integer index vectors.
The analytic path can omit the basis file. A supplied basis must contain its corner master.
The interface never receives reference coefficients.

`learned` uses the frozen batch and equation choices for native requests.
`fixed_off` uses separately tuned fixed partitions and disables all ML.
`previous` uses the preceding undivided native workflow.
`off` uses one native batch and disables all ML.
All strategies use the same analytic formula when its domain applies.

## Files and execution order

1. `s00_formula.py` defines the physical guard and exact coefficient formula.
2. `s01_study.py` checks native coefficients and high-loop Gamma ratios.
3. `s02_job.sh` submits one bounded study stage to the scheduler.
4. `s03_route.py` connects the formula to the trained native workflow.
5. `s04_native_followup.py` selects fixed seed bounds and runs new comparisons.
6. `s05_route_test.py` tests domain guards and fresh application processes.
7. `s06_document.py` makes the scientific text and timing plot.
8. `s07_readmes.py` maintains these folder guides.

Submit `s02_job.sh s01_study.py`, then `s02_job.sh s04_native_followup.py`.
Complete and freeze the batch study before running `s05_route_test.py`.
The batch study's `s11_finish.py` runs the integration test and builds both documents.
`derivation.tex` derives the formula from the one-loop convolution.
`summary.json` records the initial comparison and high-loop checks.
`native_followup/summary.json` records the stronger fixed-seed comparison.
`application/summary.json` records the final combined-interface tests.

The application test has 49 guard checks and 48 fresh process executions.
It includes process startup, imports, input/output, calculation, and exact comparison.
Its analytic requests use loops 1, 4, 8, and 12.
Its native requests repeat a declared subset of the batch study.
The application test establishes integration. It does not add unseen native graph structures.

## Limits and dependencies

The analytic calculation uses the Python standard library.
Verification uses SymPy and mpmath. Plotting uses Matplotlib.
Use the existing `.tools/seed-model/venv` environment for the complete study.
Native comparisons use the same checked Kira binary as the batch study.
The scheduler requests one worker and 8 GiB of memory.
The standalone banana comparisons limit each native attempt to 90 seconds and scratch space to 32 MiB.
The combined native path uses the batch workflow's 150-second request limit and 60-second attempt limit.
Retained files in this folder have a 2 MiB limit.
The combined project limit remains 10 GB.
Failed calculations remain in the results and receive no speedup ratio.
Read the paper for the physical definition, derivation, and measured times.
