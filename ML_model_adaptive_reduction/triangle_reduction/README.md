# Direct triangle reduction and native cost selection

This application reduces supported massless triangles with an exact formula and sends other supported inputs to its retained analytic and native methods.
The triangle has two lightlike external legs and one spacelike invariant.
The formula gives a bubble decomposition and its Gamma-function value.
Independent triangle products use the same identity through thirteen loops.
The code keeps component coefficients as products to avoid unnecessary expansion.

The native study uses planar boxes, nonplanar boxes, massive sunrise integrals, and a three-loop vacuum.
It fits a cost model from complete reduction times.
Model fitting uses 36 requests from 48 measured training requests. Validation uses 20 requests.
The additional model is disabled after validation.
The preceding learned seed policy remains active for its supported requests.
Fixed controls retain that seed policy. They isolate the added cost selector.

Use `s32_deploy.py` for one request. Its output path must remain inside this `triangle_reduction/` directory.
Use `s33_batch.py` for a list of requests.
Both commands accept `--action integrated`, `--action fixed`, and `--action previous`.
The previous action calls the published reconstruction application.
The integrated action first checks the exact triangle conditions.
It then uses the frozen native policy within its stated bounds.
Other inputs use the preceding application.

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/triangle_reduction/s32_deploy.py --case input.json --output ML_model_adaptive_reduction/triangle_reduction/requests/result.json --action integrated
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/triangle_reduction/s33_batch.py --cases inputs.json --output results.jsonl --action integrated
```

Run native reductions through the cluster scheduler on an Intel Gold compute node.
The reconstruction executable has been verified for that processor class.
The batch input contains 1 to 128 requests with distinct IDs.
Its input limit is 2 MiB. Its output limit is 8 MiB.
A batch retains loaded routines and model data. It computes each requested reduction.
Check every result's success field and confirm that every input ID has an output.
An interrupted batch can leave a partial output file.

Each input uses the preceding case format: id, group, topology_group, split, definition, targets, and size.
The definition contains loop momenta, external momenta, propagators, scalar products, and sectors.
The triangle rule requires rational spacelike invariants and massless propagators.
Each power must be between zero and four. Each triangle's total power is at most eight.
Cross-loop auxiliary powers must vanish. Cut and numerator cases use the preceding method.
The dimension remains symbolic. Pole values require dimensional continuation.

The tests contain 40 requests and three repetitions per method.
They also contain 53 earlier analytic regression requests.
The shared-call comparison uses all 93 requests in each collection.
The final measured shared-call ratio is 0.912299 against the preceding published application.
The separate core comparison ratio is 0.872521.
The final monitor tolerates files that Kira removes during storage checks.
A controlled check reproduces the old failure and confirms the corrected count.
The added equation filter increased validation time and required recovery in all ten filtered attempts.
It remains disabled. The prior seed model remains active within its accepted domain.
The first complete comparison passes 19946 coefficient comparisons.
The final serial comparison passes 13401 coefficient comparisons across 837 application results.
The earlier parallel comparison stops at one preceding-application basis mismatch.
That recovery returns 20 masters where the reference uses 16.
Its records retain 650 passing request comparisons and one failed comparison.
The parallel summary uses its two complete matched repetitions.
The final serial comparison uses all three planned repetitions.
The tests cover defined structures. They do not establish all integral types or a global optimum.

## Code sequence

- `s00_triangle_common.py` reads and writes bounded records and loads the preceding application.
- `s01_triangle.py` recognizes the triangle conditions and evaluates finite Gamma ratios.
- `s02_triangle_cases.py` defines the disjoint native splits and triangle requests.
- `s03_triangle_runtime.py` integrates the formulas and native settings.
- `s04_triangle_measure.py` measures fresh calls and compares exact coefficients.
- `s05_triangle_development.py` runs development pilots. `s06_development.sh` schedules them.
- `s07_triangle_collect.py` measures training and validation actions.
- `s08_triangle_train.py` fits and exports the model. `s09_learning.sh` schedules both steps.
- `s10_formula_checks.py` checks Gamma values, recurrences, products, and rejected inputs.
- `s11_freeze.py` freezes the model and source before testing.
- `s12_test.py` tests fresh calls and prior analytic cases. `s13_test.sh` schedules it.
- `s14_triangle_batch.py` is the shared-call application.
- `s15_batch_test.py` compares shared calls. `s16_batch_test.sh` schedules it.
- `s17_analyze.py` computes the results. `s18_plot.py` draws the report figure.
- `s19_write_report.py` writes the report sections from saved evidence.
- `s20_diagnose.py` preserves the disputed vacuum comparison. `s21_diagnose.sh` schedules it.
- `s22_guides.py` updates these guides. `s23_validate.py` checks evidence and renders both documents.
- `s24_repeat_check.py` repeats the disputed setting. `s25_repeat_check.sh` schedules those checks.
- `s26_symbolic_audit.py` checks action records against separate symbolic reductions.
- `s27_equation_runtime.py` tests the existing equation classifier with the new settings.
- `s28_equation_compare.py` measures the added filter. `s29_equation.sh` schedules the validation.
- `s30_monitor.py` counts active scratch files and tolerates concurrent removal.
- `s31_scan_checks.py` tests that behavior and preserves other access errors.
- `s32_deploy.py` is the final single-request entry. `s33_batch.py` is the final shared entry.
- `s34_monitor_test.py` compares complete collections. `s35_monitor.sh` schedules that comparison.
- `s36_monitor_summary.py` reports the final times, failures, and exact checks.
- `s37_finalize.sh` schedules analysis, figures, both documents, and validation after the tests.
- `s38_serial_test.py` repeats the final comparison with one worker and rotating method order.
- `s39_serial.sh` schedules that comparison. The final summary retains the separate parallel result.
- `s40_equation_audit.py` counts filtered equation calls and identifies the ten master-basis failures.

The new selector retains the preceding application for the three-loop vacuum structure.
A development coefficient comparison failed before the collector saved its candidate output.
The surviving log and independent diagnostics remain in this folder.
The collector saves failed outputs before stopping.

Freeze inputs and models before reserved tests. Preserve failed checks and their resolution.
Training and test data remain on Hoffman and GitHub. Keep only reports and authored support tools locally.
The resource plan bounds the new study at 20 MiB and native scratch at 32 MiB per worker.
Use at most two native workers with one computation thread each.
The combined project ceiling remains 10,000,000,000 bytes.
Publication and document rendering use separate resource reservations.

See `report/triangle_appendix.tex` for the derivation and `report/triangle_inputs.tex` for the physical test inputs.
`summary.json` gives the measured outcome. `test_protocol.json.gz` identifies the frozen comparison.
`validation.json` records the final checks and document hashes.
