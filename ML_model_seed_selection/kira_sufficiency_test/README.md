# Predicted-seed sufficiency in Kira

This experiment tests whether the frozen model's selected seeds supply enough stored identities to express each reserved target through its specified masters. It covers 690,382 targets in 5,137 test families at loop orders one through twelve. The threshold stays at 0.5. The model, candidate pools and grouped split stay fixed.

The exact Kira sufficiency test is complete for 690,382 reserved targets in 5,137 families. Predicted seeds suffice for 652,517 targets (94.515%). The full candidate pool suffices for 690,382 (100.000%), and background identities without IBP seeds suffice for 26,915 (3.899%). All symbolic decisions agree with three independent finite-field row-space checks. The model and threshold remain unchanged. This test checks existence of a reduction within the stored identity pools; it does not reconstruct all master coefficients or measure a native Kira speedup.

## Mathematical test

For each target, the selected equations include every stored IBP identity from each predicted seed. Stored partial-fraction and symmetry identities remain available as background equations. The finite source pool contains the constraints used during family generation.

Let V be the formal vector space of integrals over Q(x,d), R(S) the span of the supplied identities, and M the span of the specified master vectors. A target T has a complete reduction to these masters precisely when its coefficient vector lies in R(S)+M. Equivalently, T represents zero in V/(R(S)+M).

Kira 3.1 tests this condition through its documented user-defined-equation interface and Fermat's symbolic algebra. A public target-definition equation introduces an auxiliary variable for the weighted target expression. One unit row for each master defines the formal quotient. These rows identify master vectors with zero only in the test space; they make no assertion that physical master integrals vanish. A zero target remainder establishes sufficiency. A nonzero remainder establishes that more equations are needed. This test establishes existence of rational master coefficients without reconstructing every coefficient.

Reference seed labels, construction paths and reference master coefficients supply no equations. Different selected sets use separate copies of all variables. Targets with identical selected sets share a system within their family. Only components disconnected from every target term are removed.

Three policies use the same background identities: predicted seeds, all candidate seeds, and no IBP seeds. Independent sparse elimination reconstructs the row space from original identities at three finite-field samples and checks every symbolic membership decision. Each nonzero symbolic remainder also has an exact nonzero sample witness at regular parameter values. The sample coordinates enter after Kira finishes. The pilot additionally compares 765 policy decisions with explicit master-coefficient reductions.

The full candidate set tests the fallback for insufficient predictions. The experiment does not determine the smallest necessary addition or tune predictions from test results. Reference sets can be nonunique and need not be minimal.

The higher-loop families have dependent massive denominators. Importing the stored equations tests sufficiency within Kira's actual algebraic solver. An insufficient result refers to the stored equation pool; native generation can supply additional valid operators at the same seeds. Native Kira topology generation, unrestricted high-loop scattering families and total runtime comparisons with native seeding remain outside this experiment.

## Files and execution

s00_check_kira.py and s01_run_fixtures.sh check sufficient and insufficient small systems and independent variable copies.

s02_common.py reads frozen data, selects all identities from the predicted seeds and provides bounded rational arithmetic. s03_kira_adapter.py exports the disjoint systems, runs Kira and reads symbolic remainders. All coefficient text is compacted before import, including public target coefficients.

s04_run_pilot.py and s05_run_pilot.sh preserve the explicit master-coefficient pilot. s06_evaluate.py freezes the protocol and evaluates the complete reserved division. s07_run_evaluation.sh supplies sixteen independent single-CPU scheduler tasks. s08_verify.py checks sparse row-space membership and nonzero witnesses. s09_check_import.py and s10_run_import_checks.sh preserve the coefficient-import regression check.

s11_summarize.py and s12_run_summary.sh verify frozen hashes, source files, predictions, raw exports, policy masks, witnesses and target coverage. They create results.json, validation.json and family_results.csv only after every family completes without unresolved errors. s32_verify_export.py regenerates every actual input from the public target terms and selected source identities, verifies that all connected selected identities are present, and matches the exact input hash. input_regeneration_pilot.json records its initial checks on 211 saved systems. s13_plot_results.py and s14_run_plots.sh draw the checked figures and copy their PDFs to report/. s15_update_report.py updates the scientific text from the checked results and an immutable data-release commit.

s16_check_target_order.py and s17_run_ordering_check.sh preserve a diagnostic ordering trial. s18_check_master_span.py and s19_run_span_check.sh run three representative quotient-space pilots. s20_validate_span_pilot.py and s21_run_span_validation.sh independently verify their input regeneration, raw output hashes, 4,827 sample decisions and 765 explicit-coefficient decisions. s23_check_quotient_order.py and s24_run_quotient_order.sh preserve an alternative ordering diagnostic. That ordering left some auxiliary variables unexported and is not used in the evaluation. s25_finalize_readmes.py updates folder descriptions from checked counts, and s26_validate_reader.py reproduces the reader checks. s27_retry_small_batches.py and s28_run_small_batch_pilot.sh validate a complete 283-target box family that exceeded the initial per-file limit. Its 209 individual systems give 233 sufficient predicted sets and 283 sufficient full sets; their raw records are retained once under results/worker_14/. s29_resume_small_batches.py, s30_run_small_batches.sh and s31_pack_small_batches.py resume missing families with bounded grouped systems.

s22_coefficient_reader.py supplies a bounded nonrecursive reader for large rational expressions; reader_validation.json records comparisons with the previous evaluator.

From the project root, load the existing Python module and use the installed environment. The normal sequence for this frozen experiment is:

    qsub ML_model_seed_selection/kira_sufficiency_test/s19_run_span_check.sh
    qsub ML_model_seed_selection/kira_sufficiency_test/s21_run_span_validation.sh
    PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s06_evaluate.py --freeze
    qsub ML_model_seed_selection/kira_sufficiency_test/s30_run_small_batches.sh
    qsub ML_model_seed_selection/kira_sufficiency_test/s41_run_remaining.sh
    qsub ML_model_seed_selection/kira_sufficiency_test/s46_run_large_output.sh
    qsub ML_model_seed_selection/kira_sufficiency_test/s12_run_summary.sh
    qsub ML_model_seed_selection/kira_sufficiency_test/s14_run_plots.sh

Complete and check each stage before the next, or use scheduler dependencies. The evaluation resumes hashed completed families. Box-family execution now uses s30_run_small_batches.sh after the validated small-batch trial. s29_resume_small_batches.py preserves the same model, identities and mathematical criterion, while s31_pack_small_batches.py groups at most four independent systems with at most sixteen targets per system. execution_overrides.json and packing_validation.json record the exact source hashes and verify identical equations, targets and policy assignments. Changed scientific inputs require a new frozen experiment. Reader-only execution revisions preserve earlier code, protocol and hashes of retained results in archive_span_reader_v1/. archive_span_large_batches/ retains the states from the larger-batch execution. Resource-limit cases remain unresolved until their checked retry completes.

results/worker_XX/ stores compressed family summaries, batch manifests and raw Kira exports. Manifests record selected seed positions, source-equation IDs, weight-to-integral mappings, target definitions, unit master rows, input hashes and execution bounds. They regenerate the exact full input from the frozen canonical data without duplicating the integral collection. Raw .kira.gz exports and symbolic remainder witnesses support independent inspection.

span_pilot/, pilot/, import_checks/ and fixture_runs.json hold validation evidence. archive_coefficient_reductions/ retains the bounded initial full-coefficient attempt. Some of its harder boxes exceeded the runtime limit, which motivated the equivalent master-span criterion. A timeout or reader failure is an unresolved computation and is never recorded as seed insufficiency. ordering_pilot/ retains its separate ordering diagnostic. worker_XX.json and scheduler/ record progress and execution errors.

## Resource bounds

Each worker uses one CPU, reserves 3 GiB of scheduler memory and limits each process to 1.5 GiB of virtual memory. Each Kira case has a 600-second timeout and 64 MiB scratch limit. Temporary databases use the compute node and are removed after saving results. The initial workers have a 24 MiB compressed-output budget. Resumptions allow up to 32 MiB per worker. resource_limits.json reserves the additional output and Git copies while keeping the combined maximum at 9,925,125,760 bytes. s33_output_budget.py enforces the allowance, and s34_resume_output_budget.py with s35_run_output_resume.sh resumes finished shards without overlapping writers. s36_resume_unfinished.py and s37_run_remaining.sh finish only shards with missing results; completed shards require no repeated calculation. Coefficient parsing has a 2 MiB expression bound. The initial frozen protocol reserved 9,656,690,304 bytes combined, including the local report, worker scratch, outputs, publication copies and report work. No model training runs during this test.

Generated tests stay on Hoffman and GitHub. The report also stays on the local machine. The frozen model SHA-256 is b8fb9cc088bd4e0cbbe1168d1e5fbd733ebea361fd41d3de48827672732ed977. The split SHA-256 is 317c5167fb69424ee39b34c80290e9ed20b0ac6f208eb0adea5c681a494a5bff.

The [official Kira documentation](https://www.physik.hu-berlin.de/de/pep/tools/kira/kira-release-notes-1.2.pdf) describes user-defined systems. The [Kira 3 paper](https://arxiv.org/abs/2505.20197) describes the solver.

The final resource continuation uses s38_output_budget_48.py through s41_run_remaining.sh. resource_limits_v2.json raises the compressed allowance to 48 MiB per worker and limits the continuation to eight concurrent workers. The output and Git increase equals the released scratch reserve, so the combined bound remains 9,925,125,760 bytes. The continuation waits for preceding workers and skips every completed shard. It preserves all scientific inputs and all completed results.

s42_resume_ready.py and s43_run_ready.sh use two spare slots for finished shards while at most six preceding tasks continue. They skip any shard that still has an active writer. The final continuation waits for this job as well and resolves every deferred shard. ready_resume_schedule.json records the source hashes and combined concurrency bound.

Final resource accounting reserves 128 MiB for solver tools and nonworker artifacts, including a publication copy of those artifacts. This raises the final conservative combined bound to 9,992,234,624 bytes. resource_limits_v2.json records 52,996,096 bytes of solver tools and 32,153,600 bytes of nonworker test artifacts at the accounting check. The solver inputs and per-worker output bounds remain unchanged.

resource_limits_v3.json redistributes unused output reservations from completed workers 0, 1, 3, 13 and 15 to worker 10. Their saved files fit 32 MiB each, except worker 15 at 24 MiB. Worker 10 can use 80 MiB; the other unfinished workers retain 48 MiB. The total worker-output reserve falls to 712 MiB, and the combined bound falls to 9,874,794,112 bytes. s44_output_budget_80.py through s46_run_large_output.sh enforce and record this continuation after its preceding writer finishes. No scientific inputs change.

After the preceding active tasks fell to three, the scheduler allowance for s43_run_ready.sh increased from two to five tasks. ready_resume_schedule.json records this override; at most eight evaluation tasks remain active together.

The completed results are in results.json, family_results.csv and results/; validation.json verifies coverage and hashes. figures/ contains the two PDF figures and PNG previews. s25_finalize_readmes.py updates folder descriptions from the checked result counts.
