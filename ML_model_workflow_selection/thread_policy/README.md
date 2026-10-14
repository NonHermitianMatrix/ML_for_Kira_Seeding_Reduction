# Solver worker selection

This study tests one, two, and four Kira workers.
The preceding learned seed policy remains active.
All methods run within the same four-core allocation.
The comparison records wall time and exact results. Extra cores are a separate resource cost.

- `s00_runtime.py` applies a worker count before Kira starts.
- `s01_study.py` builds independent references and bounds saved records.
- `s02_native_runner.py` provides the internal `run` function for Kira with time, memory, and storage limits. Use `s07_reduce.py` for public requests.
- `s03_job.sh` requests four cores for one active calculation.
- `s04_probe.py` compares worker counts on development profile 91.
- `resource_plan.json` bounds combined project storage.

Use the existing Python, Kira, and Fermat installations.
Run `qsub ML_model_workflow_selection/thread_policy/s03_job.sh s04_probe.py`.
Keep data and models on Hoffman and GitHub.
The saved study has a 16 MiB limit. Active Kira files have a 32 MiB limit.

## Training and comparison

- `s05_fit.py` fits seventy complete-time predictors on profiles 92 and 93.
- `s06_test.py` compares five frozen methods on profiles 95 and 96.
- `s07_reduce.py` applies the frozen worker choice to a case and prescribed basis.
- `s08_analyze.py` checks exact records and summarizes wall time, CPU time, and memory.
- `s09_pipeline.py` trains, validates, freezes, tests, and checks public applications.
- `s10_public_checks.py` tests seven public applications without target coefficient inputs.

Profile 94 supplies validation measurements.
The test compares native one-worker choices, the preceding one-worker route, the preceding route with four workers, a fixed setting per graph, and the selected route.
The reported CPU time includes the Python worker and waited-for child processes.
The reduction timer includes model decisions, input preparation, exact reduction, checks, retries, and cleanup.
Model loading and offline data preparation remain separate.
Run `s09_pipeline.py` after the development probe supports proceeding.

Validation minimizes the sum of complete batch times.
A new predictor must save at least two percent against the faster control.
It must also win in two of three validation repetitions.
The model is frozen before any reserved test.
Target index patterns overlap across splits. Kinematic values differ.
This test does not measure transfer to new graphs or new target patterns.

- `s11_validate.py` checks exact results, source versions, data splits, and resource limits.
- `s12_write_report.py` writes measured results and the appendix into both documents.
- `s13_finish.py` runs those checks, updates folder guides, and renders both PDFs.
- `thread_policy_appendix.tex` explains worker choices, labels, exactness, and timing.

Run the training job with `s09_pipeline.py --train-only`.
Run the test job after it finishes with `s14_test.py`.
The original `s09_pipeline.py --test-only` remains an equivalent, slower record-writing path.
Run `s13_finish.py` after all tests finish.
Use the `s03_job.sh` wrapper for each step.
Keep one scientific job active at a time.
The resource monitor limits each native attempt to 2.1 GiB RSS and 120 seconds.
The public interface accepts one request at a time.
Pass a JSON input with `case` and `basis` fields to `s07_reduce.py --input INPUT --output OUTPUT`.
The retained frozen policy selects at most two workers. Use the two-core application wrapper for public requests.

- `s14_test.py` runs the frozen test with bounded record writing. It scans storage every 32 writes and reserves one MiB for metadata growth. Record writing stays outside the reduction timer. `test_writer.json` records this harness version before testing.

## Consecutive requests

- `s15_worker.py` reads one JSON request per input line and writes one result per output line.
- `s16_worker_checks.py` checks seven consecutive requests against independent exact reductions.

Run `s15_worker.py` in a dedicated Python process on an allocated compute node.
Each request has `case` and `basis` fields, as in the public input examples.
Keep the process open between requests to retain the loaded models.
The worker starts fresh Kira attempts for each request.
It processes requests in sequence and does not use reference coefficients.
The input limit is one MiB per request and four MiB per session.
The output limit is sixteen MiB per session, with at most 128 requests.
Each request can contain at most 128 targets.
Run `s16_worker_checks.py` after the single-request public checks.
The final document step includes these checks.
The reserved comparison times loaded models; fresh command-line startup has a separate cost.

- `s17_application.sh` runs the persistent worker in a two-core allocation.

Run `qsub ML_model_workflow_selection/thread_policy/s17_application.sh REQUESTS.jsonl` from the project root.
Use one `case` and `basis` request per line in `REQUESTS.jsonl`.
The job writes JSON results to its scheduler output.
Keep request files and results on Hoffman.
The fixed model can choose only one or two workers; its exact fallback also uses one worker.
The separate benchmark reserves four cores to test the always-four-worker control.
The seven persistent-worker checks use a two-core allocation with the same four-GiB total scheduler memory request.

## Completed comparison

All 900 timed reductions and 50 further applications pass exact checks. The selected method gives 1.8 percent less full time than the preceding method and 15.4 percent less than native choices. These are geometric means with equal graph weights. See `model_test/summary.json` and the paper for each graph, all regressions, timings, and limits. The test covers known graphs and target patterns with new parameter profiles.
