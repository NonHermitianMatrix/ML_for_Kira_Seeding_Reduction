# Reduction-model test

This folder tests the saved thirty-epoch reduction-propagation model on the existing reserved families. It preserves the trained parameters, grouped split, feature definition, action rule and returned probabilities. The test performs zero optimizer updates and fits no confidence map.

The same reserved set previously evaluated the ten-epoch model. This is a repeated evaluation after a user-specified twenty-epoch continuation with unchanged training settings. The test records remain excluded from gradient updates. The previous evaluation is preserved at commit c2ba11c579c8851a22c69132e36a03f9ba4aa8b7; active results and figures refer to the thirty-epoch weights.

The inputs comprise 307 families and 72,142 targets from integrals/testing/. The current split_manifest.json in ML_model_seed_selection/ is authoritative; original split labels in older target records describe earlier dataset divisions. The held-out set has 306 one-loop families and one massless two-loop propagator family. Shared lower-sector structure and repeated box topology limit the scope of the family-transfer claim.

## What the test measures

At every recorded state, the model receives the current target row and the complete stored candidate list. The test records every action probability and compares the chosen equation with the recorded equation. Main accuracy, top-three, top-five, reciprocal rank, Brier score, negative log probability and confidence-bin results exclude forced states. Equality of the sampled next row is a separate metric because different equations can have the same effect. All-state results and forced counts remain available.

A softmax tie uses the trained interface's fixed equation-ID order. tie_metrics.json also reports the expected top-one agreement if tied maxima were selected uniformly. This is an additional descriptive metric; it does not change predictions or paths.

For complete reductions, each policy starts from the target row and receives its own updated row after every action. The pivot is its largest remaining nonmaster integral under the recorded integral order. Candidate rows come from the full stored identity pool with that leading integral and a valid sampled pivot. The test checks that this rule reconstructs the recorded candidate lists. No later reference state or master coefficients enter the policy.

The fixed local comparison rule tries each candidate and minimizes, in order, the resulting nonmaster term count, total nonzero count, source-row operation count and equation ID. The learned and local policies use the same initial rows, masters, equation pools and pivot order. They run in alternating order by target. A path can complete, run out of allowed equations or exceed fixed row, input or step limits. There is no reference-path fallback.

Each chosen row operation is checked by exact cross multiplication. Its sequence of identities is then replayed from the original symbolic target and identity coefficients at all three stored points and primes. A successful target must complete and reproduce the saved master coefficients at every sample. Singular source pivots count as unverified. These finite-field checks do not reconstruct a symbolic answer or prove a globally minimum path.

Committed cost counts one division plus one multiplication and subtraction per nonzero source coefficient. Candidate trial updates contribute a separately recorded cost. total_field_operations sums those two counts; it excludes network arithmetic, bookkeeping and extra verification. Operation plots compare the same targets successfully completed by both policies, excluding zero reference-cost targets.

Runtime includes current-state construction, candidate selection, exact updates and per-step row checks. It excludes file access, building the source pool and the later three-sample replays. Mean and median times include unsuccessful attempts. This is a measured comparison of the current target-row implementations, not a Kira benchmark.

## Files

- test_config.json: fixed weights hash, test definitions, confidence bins and bounds.
- evaluation_request.json: checkpoint epoch, earlier commit and repeated-test provenance.
- checkpoint_validation.json: current model, optimizer checkpoint and training-history consistency checks.
- families/<family>/predictions.npz: every recorded-state probability and metric.
- families/<family>/trajectories.jsonl.gz: chosen equations, confidence, exact final rows, three-point checks and costs for every complete or unsuccessful attempt.
- families/<family>/summary.json: family counts, metrics and source/artifact hashes.
- test_results.json: aggregate state, target, loop-order, cost and time results.
- family_metrics.json and family_metrics.csv: per-family results.
- target_metrics.jsonl.gz: compact target results; full paths remain in family archives.
- additional_sample_failures.json: completed local-rule paths that failed additional sample checks.
- confidence_reliability.csv and tie_metrics.json: confidence and tie analysis.
- paired_comparison.json: common successful-target cost comparison.
- validation.json and metric_checks.json: independent replay and metric checks.
- figures/: six PDF and PNG plots. Matching PDFs are copied into report/figures/.
- figure_manifest.json and figure_values.csv: figure hashes and summary values.
- report_template.tex and report_values.json: scientific text and the values inserted into report/reduction_test.tex.
- report_validation.json: report and figure hashes and build checks.
- status.json, scheduler.log and finalize.log: progress and scheduler output.
- pilot.json: two-family bounded trial under the unchanged full-test protocol.

The NPZ probability arrays use offsets to delimit one action list per state. action_ids and probabilities share this flattened order. reference and predicted index that state's action list. target_number indexes target_ids, and step_number identifies the recorded step. same_row compares the selected result with the recorded next sampled row. probabilities are float32; IDs are Unicode arrays. Open archives with allow_pickle=False.

Every trajectory record contains model and greedy results. Each path step retains its equation, pivot, confidence (model only), candidate count, row sizes and committed/trial operation counts. final_row and sample_checks retain the coefficients needed to inspect success or failure. Reference costs are known valid upper bounds under the stated convention; the test does not call them optimal.

## Scripts and execution

1. s00_test_common.py: fixed provenance, bounded output, exact coefficient evaluation and metric definitions.
2. s01_policies.py: candidate pools, fixed local comparison rule, autonomous paths and three-sample replay.
3. s02_evaluate.py: frozen recorded-state predictions and complete-path evaluation; resumes unchanged completed family outputs.
4. s03_check_metrics.py: analytic probability and finite-field checks.
5. s04_run_test.sh: bounded scheduler wrapper for the checks, two-family pilot and complete held-out evaluation.
6. s05_validate_outputs.py: independently recompute metrics, replay all chosen paths with Fermat inversion, verify source and artifact hashes, and repeat representative frozen predictions.
7. s06_plot_results.py: create the six figures and paired comparison.
8. s07_update_report.py: insert validated measurements into the report and READMEs; --validate-build checks the rendered report.
9. s08_finalize_report.sh: scheduler wrapper for validation, plots, report generation and PDF build.
10. s09_validate_checkpoint.py: verify the thirty-epoch model against its saved optimizer checkpoint and training provenance.

From the project root:

    qsub ML_model_reduction/model_test/s04_run_test.sh
    qsub -hold_jid <evaluation-job-id> ML_model_reduction/model_test/s08_finalize_report.sh

The finalizer requires complete evaluation and fails if required outputs are absent. The evaluator checks hashes before reusing a completed family. Changes to the model, input split, encoder, predictor, test configuration or producer scripts require a separately identified evaluation; existing results are never silently accepted under changed provenance.

Both jobs request one CPU and 4 GiB. They cap virtual memory at 3 GiB and a single output file at 128 MiB. A family output has an additional 64 MiB limit. Reduction paths have at most 4,096 steps and 4,096 current-row nonzeros. The existing model and combined project storage guards remain active. Keep these records on Hoffman and GitHub only; synchronize only the report and its figures to the local report folder.

<!-- test-results:start -->
The frozen thirty-epoch reduction model was tested on 72,142 targets in 307 held-out families. It matched 94.716% of recorded choices on 194,347 states with at least two actions. Complete learned paths matched all three sampled master expansions for 72,088 targets; the fixed local rule passed 71,463. Mean attempted reduction times were 10.0639 ms and 0.4643 ms, respectively. Reference paths are valid without a proof of minimality. These are target-row tests; no full Kira speedup was measured.
<!-- test-results:end -->
