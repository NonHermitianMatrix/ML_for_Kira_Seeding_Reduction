# Reduction-propagation model

The model scores the supplied allowed source-row eliminations at the current target row, returns a probability for every action and selects the highest-scoring action with its estimated confidence. The exact solver performs the selected finite-field operation. It has 10,529 parameters and 132 input features per action.

The current checkpoint completed twenty new passes over 1,610,890 training targets from 11,963 complete families. Every loop order from one through twelve occurs in training. The fixed test division contains 690,382 targets from 5137 families. New mass profiles remain in one split across all loop orders; earlier assignments are preserved. The higher-loop families are restricted coupled vacuum integrals. Both splits share some lower-sector physics and every loop order. Reference seed sets and paths are sufficient; their minimality is not proved.

s00_common.py, s01_state.py and s03_model.py define file guards, exact row features and the neural scorer. s02_prepare_data.py replays training traces and creates bounded state files using four allocated workers, after exact comparison with saved training arrays. s10_train_all_loops.py continues the saved weights and optimizer for twenty expanded-data passes; s11_run_all_loops.sh runs preparation and training. s05_predict.py exposes prediction and optional exact row application. Earlier s04 and s06 through s09 scripts preserve the initial workflow.

trained_model.pt stores the current inference model; trained_model.json records measured training results. runs/all_loops_latest.pt retains the optimizer and exact resume position, and runs/all_loops_history.json records all twenty new passes. runs/before_expansion_250/ preserves the preceding weights, optimizer, metadata and source. The saved lineage records the earlier dataset progress separately. validation.json and release_manifest.json verify the current model. data/ contains only encoded training examples, with source hashes and the held-out count recorded separately.

Training uses four CPU threads, while inference retains one thread. A training-only trial verified score and gradient agreement. Storage checks run every 64 family groups; every checkpoint retains its 8 MiB bound. Training retains the preceding twenty-pass expanded-data weights and AdamW state, together with the earlier thirty-pass lineage, learning rate 0.001, weight decay 0.0001, gradient norm limit one and state batch bounds. Only states with multiple allowed actions contribute ranking loss. The experiment changes one target row against fixed source identities; it does not benchmark a complete Kira elimination system.

The frozen expanded-data test is complete. model_test/archive_before_expansion_250/ retains the preceding tests and their exact source. Current tests and plots occupy model_test/; the report is updated from these checked records. Generated data, model files and tests stay on Hoffman and GitHub; the report also stays on the local machine. Jobs bound CPU use, virtual memory and output sizes, and enforce the combined 10 GB ceiling.
The training metadata records the state at training completion; release_manifest.json records the current publication and test stage.

Prediction uses s05_predict.py state.json --apply --output prediction.json with the existing .tools/seed-model/venv/bin/python after loading the Hoffman Python 3.9.6 module. The input gives prime, public family information, sparse rows, row_roles, master_columns and supplied actions. Each action contains id, source_row, destination_row and pivot_indices. The optional --apply flag performs the selected exact modular row update. Source rows must represent zero identities and pivots must be nonzero.

The 132 action features describe pivot indices, row support, candidate cancellations, immediate arithmetic and public family information. A sparse modular trial update supplies local counts for each action; future trajectories and recorded selected-action IDs do not enter predictive features. The interface accepts multiple destination rows, while current training uses one changing target row. Limits are sixteen indices, 10,000 rows, 10,000 actions, 250,000 matrix entries and 4,096 entries per row.

<!-- expanded-test-results -->
The frozen model was tested on all 690,382 targets in 5137 held-out families. Recorded-action top-one agreement on choice states is 95.845215%; top-three agreement is 99.980223%. Averaging credit over highest-scoring ties gives 74.506270% agreement; the tied fraction is 37.747062%. The selected action gives the same next sampled row in 95.845528% of choice states. The learned policy matches all three sampled master expansions for 690,302 targets, and the local comparison rule does so for 689,700. Mean attempted reduction times are 12.343829 ms and 0.699096 ms, respectively.

The model changes one target row against fixed source identities. The local rule minimizes the next nonmaster count, total row support, immediate operation count and fixed equation-ID tie-break in that order. Three finite-field samples check complete paths. The test establishes neither global path minimality nor a full Kira runtime improvement.

See model_test/README.md for the complete frozen protocol and artifacts.

<!-- kira-cost-comparison -->
[Kira_comparison](../Kira_comparison/README.md) applies the frozen row model to symbolic target-row operations and sends remaining terms to Kira. The local rule uses the same adapter. The comparison is complete and independently checked. The main experiment contains 792 trials in 19 family cases; the direct native seed-bound comparison contains 84 trials in seven independent-basis families. Against Kira with the full stored source pool, learned seeds have geometric mean complete-process/prepared-input time ratios 1.720/1.116, and learned rows have ratios 1.719/1.205. Learned native seed bounds have ratios 1.596/1.344 against default native bounds and 1.671/1.373 against restricted native bounds. Against the control with seed bounds taken directly from target indices, the native learned ratios are 1.425/1.141. Ratios use matched case medians from three repeats; values below one indicate lower time. Complete-process time includes loading, inference, exact algebra, fallback and coefficient checks. Prepared-input time excludes family and model loading. Completion counts, all resource outcomes, individual cases and operation measures appear in summary.json and native_seed/summary.json. The direct native test learns sector envelopes. The row comparison in that experiment uses fixed source identities and changing target rows; the live-matrix comparison below tests changing identity rows inside Kira.


<!-- kira-live-matrix -->
## Live matrix comparison

Completed 84 final trials in seven held-out independent-basis families, with 0 incomplete trials. The learned/stock complete-time ratio is 1.305. The learned/instrumented-native forward-stage ratio is 276.149, or 62.270 after subtracting recorded model loading. Summed median committed coefficient-operation counts are 5771 for the learned policy and 5070 for the native policy.

The code, frozen protocol, exact operation records and plots are in [Kira_comparison/live_matrix](../Kira_comparison/live_matrix/). The model acts inside Kira's symbolic forward phase on changing identity rows. The report distinguishes this test from the earlier fixed-source target-row procedure.

<!-- native-acceleration -->
The native integration in [Kira_comparison/acceleration](../Kira_comparison/acceleration) filters individual IBP seeds before generation and evaluates the unchanged row network in Kira's process. The reserved comparison has 720 planned records, 616 measured trials and 590 exact completions; remaining repeats after a failed trial are explicitly skipped. ml_lower: complete-time ratio to restricted native Kira 1.295050 (descriptive 95% interval 1.156164–1.542104, 20 complete paired batches); 100 exact completions, 4 failed trials and 16 skipped repeats. row_cpp: complete-time ratio to restricted native Kira 1.023629 (descriptive 95% interval 0.998189–1.053330, 21 complete paired batches); 105 exact completions, 3 failed trials and 12 skipped repeats. combined: complete-time ratio to restricted native Kira 1.983350 (descriptive 95% interval 1.574863–2.476497, 15 complete paired batches); 75 exact completions, 9 failed trials and 36 skipped repeats. All ratios include complete checked calculation time on complete paired cohorts. The report gives the controls, failures, descriptive intervals and one-loop scope.

<!-- whole-expression-confirmation -->
The whole-expression interface uses the frozen seed model, Kira's early master check, exact supplied-equation reduction and full-pool fallback. The reserved comparison contains 360 planned records, 348 measured trials and 345 exact completions. Its complete-time ratio to the full-pool supplied-equation control is 0.943782 (descriptive 95% interval 0.863046–1.041560; 23 complete paired batches), and its ratio to the fixed 64-seed distance control is 0.603585 (descriptive 95% interval 0.534379–0.677998; 23 complete paired batches). The full-pool control completed 0 additional batches and the learned method completed 0 additional batches. Both comparisons start from the same existing identity pool and include loading, prediction, equation export, exact algebra, failed attempts, fallback and checks. Offline pool generation is outside both measurements. These are constructed targets from twelve original-held-out one-loop box instances in six kinematic groups.

The separate two-loop transfer has 60 exact completions. For 64 targets the compiled learned-row pipeline took a median 12.460 seconds against 12.770 seconds for restricted native Kira, a 2.4% reduction. Its advantage over the deterministic compiled source control remains unresolved, and the full-pool control was faster at 11.773 seconds. Both seed-containing policies required fallback in every 64-target repeat.

Code, raw measurements and checks: [../Kira_comparison/acceleration](../Kira_comparison/acceleration).

<!-- matched-admission-confirmation -->
The additional matched-admission confirmation applies the same early master check and full-pool fallback to learned seeds and the 64-seed distance control. It contains 360 planned records, 348 measured trials and 345 exact completions. The learned complete-time ratios are 0.931643 (descriptive 95% interval 0.844721–1.030866; 23 complete paired batches) against the full pool and 0.925206 (descriptive 95% interval 0.847770–1.023721; 23 complete paired batches) against the matched distance control. The full-pool control completed 0 additional batches, and the learned method completed 0 additional batches. This repeats the same twelve physical family instances; it is not a new-family test. The first comparison is fully retained, and its distance control lacks the early admission check.

<!-- single-target-result -->
The predefined single-target comparison gives 8.6% lower geometric mean complete time against the full-pool Kira control and 8.7% lower time against the distance control with the same early check. Both descriptive intervals lie below one across all twelve held-out instances, with five exact repeats per method. The earlier confirmation gave 7.8% lower time against the full pool for this batch size. The sixteen-target intervals include one. This measured benefit applies to one constructed target expression at a time using an existing IBP identity pool; it does not establish a native Kira or general high-loop speedup.

<!-- native-multiloop-results-begin -->
## Complete multiloop cost comparison

The fixed complete-generation experiment has 324 planned workflows, 324 measured workflows and 324 exact completions.

The selected seed policy's complete-time ratio to responsive stock Kira is 0.741945 (12 paired batches).

Seed-to-stock time ratios are 0.563457 for two-loop boxes, 1.265710 for three-loop vacua, 0.572691 for three-loop ladders. The aggregate seed time interval includes one; gains are specific to the tested family classes. The row-time interval also includes one.

The cost-trained row policy's complete-time ratio to instrumented native Kira is 1.007901 (12 paired batches); its forward coefficient-operation ratio is 1.003162 (12 paired batches).

These are paired, three-repeat comparisons at rational kinematics with symbolic d. Results include inference, native generation, exact algebra, verification and fallback. The common reference basis is prepared separately.

The independent audit passed. Family-level results and completion counts must accompany aggregate ratios; none establishes a universal speedup.

[Methods, raw evidence and outcomes](../Kira_comparison/multiloop_native/README.md). Original integral records and neural checkpoints remain unchanged.
<!-- native-multiloop-results-end -->

## Integrated runtime extension

The ongoing native integration extension is documented in [integrated_runtime](../Kira_comparison/integrated_runtime/README.md). It preserves previous trained models and comparisons, verifies faster seed feature construction, develops row policies from measured exact trajectories and compares complete workflows with matched native controls. New weights and measurements remain separate from earlier frozen results.


<!-- integrated-runtime-current -->
The current native-integration extension is in Kira_comparison/integrated_runtime/. It combines compiled seed inference, complete-trajectory row policies and matched native/deterministic controls. The model additions are in ML_model_seed_selection/runtime_inference/ and ML_model_reduction/runtime_training/. The initial comparison completed all 560 workflows. A 400-workflow implementation confirmation on the same eight physical profiles also completed every target with exact reference agreement. In the confirmation, seed, row and combined complete-time ratios to the smaller native control are 1.154805, 0.998979, 1.159119. The seed ratio for boxes is 0.963700; the aggregate row operation ratio is 0.985327, but its forward-stage time ratio is 1.041202. Neither model has a universal runtime advantage. Read summary.json and pair_reserved_summary.json for grouped intervals, topology results and all failed attempts. Earlier data, checkpoints and tests remain preserved. See that folder's README for the integration entry point, exact checks, resources and reproducible execution order.
