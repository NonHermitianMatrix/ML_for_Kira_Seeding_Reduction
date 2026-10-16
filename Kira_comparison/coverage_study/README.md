# coverage study

This study tests a finite grid. It does not cover every integral or unlimited loop orders.
The native grid has 90 requests. The current interface accepts 54 requests.
Read `summary.json` for exact completions, failures, paired time totals, and unsupported inputs.
The native runs generate IBP identities. The vacuum runs use supplied Euler and mass identities.
Keep these two comparisons separate. Existing models remain frozen.

Run all calculations on Hoffman with the existing Python environment.
Use `s02_job.sh` through `qsub`. Run one job at a time.
Keep the memory, time, and storage limits in `resource_plan.json`.

`s00_cases.py` defines physical denominators and target indices.
`s01_study.py` freezes the native protocol and runs the comparisons.
`s02_job.sh` supplies the scheduler limits.
`s03_vacuum.py` compares original Kira, identity selection, and exact recurrence through twelve loops.
`s04_original_runner.py` is the bounded runner with the original executable allowed.
`s05_analyze.py` checks results and draws the figures.
`s06_report.py` writes the scientific sections and these guides.
`s07_finish.py` builds both documents and checks publication inputs.

`s08_nontrivial.py` adds separate massive two-point batches with up to two dots.
`s09_family_names.py` resolves unique exact definition matches and checks the two corrected family names.
Use its `--case`, `--basis`, and `--output` options to run a new supplied-basis request.
Run it without options to repeat the recorded name checks.
Use the execution order: development pilot, native study, vacuum study, additional batches, name checks, analysis, document build.
The native study accepts `--pilot` for its small development check.
The saved protocols fix the models and inputs before timing. Do not tune a policy from these tests.
The original runner uses the saved Kira executable with custom optimization flags cleared.
A full request discovers its master basis. An application request receives the checked basis.
Reported paired ratios exclude failed, unsupported, and identity-only requests. The coverage record retains them.
`s10_audit_coefficients.py` checks saved vacuum coefficients with symbolic algebra and the analytic oracle.
The finish script runs this check before the analysis and document build.

Generated data stay on Hoffman and GitHub. Copy only the report artifacts locally.
See [native coverage](../../report/paper_figures/coverage_grid.pdf) and [matched times](../../report/paper_figures/coverage_times.pdf).
