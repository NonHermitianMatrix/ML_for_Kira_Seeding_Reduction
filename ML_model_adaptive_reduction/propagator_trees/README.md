# Exact connected two-point reductions

Use this folder for the current combined application.
It reduces supported massless two-point trees with an exact formula.
It then uses the preceding triangle formulas, other exact rules, and trained native Kira choices for other inputs.
This extension does not fit a new ML model.

Run from the project root on a compute node:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/propagator_trees/s02_runtime.py --case CASE.json --output ML_model_adaptive_reduction/propagator_trees/requests/answer.json.gz --method integrated
```

The input uses the same definition and target format as loop_coverage13.
Use --method previous to disable the new two-point formula.
Use --method all_fixed for the separate native comparison with fixed choices.
The all_fixed control is intended for the native test group; its older triangle path is not the timing control for triangle requests.
Do not run scientific calculations on a login node.

## Domain and method

The graph must be a connected tree of massless two-line subintegrals with one off-shell external momentum.
The code checks the momenta and powers before applying the formula.
The external root power, connecting powers, and leaf powers must be positive integers.
A squared-momentum power at a vertex with children can be zero or negative.
All auxiliary powers must be zero.
The current code accepts one through thirteen loops and absolute powers at most sixteen.
The external momentum square must be nonzero and can remain symbolic as s.
Cuts, symbolic indices, masses, and other graphs use the preceding application.

The calculation integrates each leaf and transfers its effective power to the parent.
The root is a final bubble integral.
The ratio to the unit-power master gives rational coefficients in d and s.
The code cancels equal Gamma factors before it forms finite products.
The paper derives this formula and states its domain.

The installed Kira build accepts at most 31 integral indices.
A complete family requires L*(L+1)/2 + L*E indices, where E is the number of independent external momenta.
This gives a seven-loop limit for complete vacuum coordinates, a six-loop limit for one external momentum, and a five-loop limit for two or three external momenta.
The exact rule avoids this native input for its supported graphs.
It does not remove the native limit for every graph.

## Files and execution order

- s00_prop_common.py loads the preceding code and limits stored output.
- s01_propagator.py checks the analytic domain and computes exact coefficients.
- s02_runtime.py runs the combined application.
- s03_prop_cases.py defines complete coordinates and separate target assignments.
- s04_prop_checks.py checks Gamma products, native reductions, and rejected inputs.
- s05_job.sh supplies one bounded scheduler job with one CPU thread.
- s06_protocol.py fixes test inputs, source records, controls, repeats, and time limits.
- s07_measure.py runs one of two test workers and checks coefficients after timing.
- s08_analyze.py separates matched timings from failed controls.
- s09_document.py writes the paper section, appendix, plots, and matching notes.
- s10_prepare.py runs the final checks and fixes the protocol.
- s11_guides.py writes these guides.
- s12_validate.py builds both documents and checks the completed study.
- s13_finish.py makes the final documents and guides after both test workers finish.

Use s10_prepare.py before the measurement workers.
Run s07_measure.py 0 and s07_measure.py 1 in separate jobs after preparation completes.
Run s13_finish.py only after both workers complete.
Keep existing results before repeating any study command.
Never start more than two native test workers at once.

protocol.json.gz contains the complete reserved cases and fixed settings.
development.json stores the mathematical and native development checks.
setup_revision.json explains development changes made before reserved tests.
native_index_limit.json records the installed source guard and its loop-count implications.
model_application_audit.json records which learned settings appear in the saved native outputs.
execution_resources.json records the scheduler exit status and resource use.
results/ stores full outputs, times, success flags, and checks.
summary.json gives the combined measured results.
validation.json identifies the sources and PDFs checked together.
resource_plan.json bounds total project storage below 10 GB.
The scheduler caps memory. No training data or research outputs are copied to the laptop.

## Results

The new rule completes 34 of 34 reserved two-point requests in all three repetitions.
The preceding application completes 3 in all repetitions.
On the 3 matched requests, complete time falls from 11.185065 to 0.432508 seconds.
These sums use three-run request medians.
Failed controls remain in the completion counts and do not receive speedup factors.

All 714 independent reserved Gamma checks pass.
The native ML comparison gives new-to-fixed time ratio 0.937102, with request interval [0.8526157963241734, 1.0100634655467022].
This interval includes equal time, so this fresh sample does not resolve a reliable ML gain.
The saved Gamma error divides the absolute difference by max(1, absolute reference value). This is the scaled error used in the paper.
The new two-point gain comes from exact algebra. The trained native models remain unchanged.
The study does not establish coverage for every integral type or minimum possible time.
