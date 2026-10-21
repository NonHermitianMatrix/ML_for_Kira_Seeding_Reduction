# Exact preparation around the learned portfolio

This experiment uses the frozen models from `../selective_expansion/`.
It restricts sector polynomials before construction and reuses unchanged selected equations within one reduction.
The models and their action choices stay unchanged in this comparison.
The revised method takes 64.183 seconds against 79.784 seconds for the previous implementation.
These totals sum the batch medians of three repetitions on 26 fresh batches.
Read `summary.json` for fixed controls, CPU times, regressions, and individual results.
All 312 timed reductions and 26 additional applications pass exact reference checks.

Use `../s24_parametric_runtime.py --case CASE.json --basis BASIS.json --output RESULT.json.gz` inside a scheduled job.
Use the same case schema as `protocol.json`. The basis file contains a JSON list of integer index vectors.
The application receives no reference coefficients. It reports failure if bounded recovery cannot complete the reduction.
Keep the model files, source files, and the two native builds at their recorded versions.
Cuts, symbolic propagator powers, and positive indices outside the declared sector domain are unsupported.
The public interface rejects invalid index types and out-of-domain targets.

Run `../s22_build_parametric.py` to build from the existing bounded Kira toolchain.
This creates `../s23_parametric_runner.py` and a separate native executable under `.tools/kira-parametric/`.
The build preserves the previous executable and records the exact source patches in `integration/`.
`../s25_parametric_job.sh` runs one two-core job with an 8 GiB memory allocation.
`../s27_profile_parametric.py` and `../s28_profile_selection.py` record development phase costs.
`../s29_check_replay.py` checks replay, forced storage bypass, zero targets, and input guards.
`../s26_parametric_study.py` fixes the new test protocol and runs references, comparisons, and applications.
`../s30_analyze_parametric.py` audits results and draws the comparison plot.
`../s31_report_parametric.py` writes the paper sections and folder guides.
Build both PDFs after the report writer. Then run the paper checker.

`development/` contains earlier preparation trials and the replay checks.
`references/` contains expanded-seed reductions and checks with the previous executable.
`model_test/` contains complete timing records for each method and repetition.
`applications/` contains requests that received only targets and the master basis.
`application_test/` contains input guards and the analytic zero check.
`integration/` contains the build instructions and source patches.
`protocol.json` fixes cases, sources, models, and comparison conditions before testing.
`resource_plan.json` bounds storage and resource use. `jobs.json` records only this study's jobs.
The logs preserve the development and completed calculation outcomes.

Each native attempt has a 6 GiB address limit, a 5,200 MiB process-tree RSS limit, and a 32 MiB scratch limit.
Selected-equation reuse allows at most 4,096 rows and 4 MiB of accounted payload, with bounded container overhead.
`KIRA_SELECTED_CACHE_BYTES=1` forces the tested storage-bypass path.
Do not change the frozen policy from test outcomes. Store generated data only on Hoffman and GitHub.
The complete project must stay below 10,000,000,000 bytes across cluster and local files.
