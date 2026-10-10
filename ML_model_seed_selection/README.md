# Seed-selection model

The model gives each supplied candidate seed a separate reference-membership probability, a binary label at p>=0.5 and the probability of the returned label. Several seeds can receive label one. It uses the symbolic target terms, every ordered pair of distinct terms, public family information and the chosen master indices. It has 28,097 parameters.

The current checkpoint completed twenty new passes over 1,610,890 training targets from 11,963 complete families. Every loop order from one through twelve occurs in training. The fixed test division contains 690,382 targets from 5137 families. New mass profiles remain in one split across all loop orders; earlier assignments are preserved. The higher-loop families are restricted coupled vacuum integrals. Both splits share some lower-sector physics and every loop order. Reference seed sets and paths are sufficient; their minimality is not proved.

The active sequence is s12_prepare_features.py (training-only encoded features), s13_batch.py (masked batch calculation and comparisons with the original score function), s14_train_all_loops.py (twenty-pass continuation), s15_run_all_loops.sh (bounded scheduler wrapper), s16_validate_all_loops.py (checkpoint and source validation), s17_run_batch_pilot.sh (bounded execution pilot), and s18_validate_mixed_batches.py with s19_run_batch_validation.sh (mixed-target score and derivative comparisons). Earlier scripts s00 through s11 preserve the initial preparation and training workflow.

trained_model.pt stores the current inference model; trained_model.json records measured training results. runs/all_loops_latest.pt retains the optimizer and exact resume position, and runs/all_loops_history.json records all twenty new passes. runs/before_expansion_250/ preserves the preceding weights, optimizer, metadata and source. The saved lineage records the earlier dataset progress separately. validation.json and release_manifest.json verify the current model. data/ contains only encoded training examples, with source hashes and the held-out count recorded separately.

The new phase uses batches of 32 targets and four CPU threads for training. Inference retains one CPU thread. The training-only resource trial verified score and gradient agreement across thread counts. An equivalent complete storage scan reduced filesystem overhead; runs/storage_scan_resume/ proves unchanged predictive code, features, configuration and exact checkpoint continuation. Factoring the first score layer avoids repeated target-context matrix multiplications without changing the network function. Direct comparisons with the original interface verify scores, loss and gradients. AdamW retains the previous optimizer state, learning rate 0.001 and weight decay 0.0001; the gradient norm is bounded by one. Scores describe membership in one reference seed set, and this model test alone does not run Kira with the predicted sets.

The frozen expanded-data test is complete. model_test/archive_before_expansion_250/ retains the preceding tests and their exact source. Current tests and plots occupy model_test/; the report is updated from these checked records. Generated data, model files and tests stay on Hoffman and GitHub; the report also stays on the local machine. Jobs bound CPU use, virtual memory and output sizes, and enforce the combined 10 GB ceiling.
The training metadata records the state at training completion; release_manifest.json records the current publication and test stage.

Prediction uses s04_predict.py --checkpoint ML_model_seed_selection/trained_model.pt --target FAMILY:ID, with an optional --seeds file containing an indices list. Run it with the existing .tools/seed-model/venv/bin/python after loading the Hoffman Python 3.9.6 module. The output includes predicted_label, probability_1, probability_0 and confidence for every candidate, ranked by probability_1. The public prediction path reads no reference labels.

The shared network uses 32-component hidden descriptions and a 64-component score layer with tanh activations. It compresses symbolic coefficient tokens into 64 signed hash components, which permits collisions. Ordered combinations mean all ordered pairs of distinct stored terms. Inputs accept at most sixteen indices, 512 terms and 10,000 supplied candidates. The candidate list is a bounded pool, and the chosen master basis is public input. Family IDs, split labels, reference coefficients, construction histories and future operation counts do not enter the scores.

<!-- expanded-test-results -->
The frozen model was tested on all 690,382 targets in 5137 held-out families. At the fixed threshold 0.5, pooled precision is 95.750448%, recall is 96.892412%, F1 is 96.318045%, and complete reference-set agreement is 84.332297%. Mean target average precision is 99.090018%.

The labels identify one sufficient reference seed set. Alternative sufficient sets can differ, and this evaluation does not run Kira with the predicted sets or establish globally minimal seeds. Candidate-label accuracy must be read with the sparse positive-label fraction.

See model_test/README.md for the complete frozen protocol and artifacts.

<!-- exact-kira-sufficiency -->
The exact Kira sufficiency test is complete for 690,382 reserved targets in 5,137 families. Predicted seeds suffice for 652,517 targets (94.515%). The full candidate pool suffices for 690,382 (100.000%), and background identities without IBP seeds suffice for 26,915 (3.899%). All symbolic decisions agree with three independent finite-field row-space checks. The model and threshold remain unchanged. This test checks existence of a reduction within the stored identity pools; it does not reconstruct all master coefficients or measure a native Kira speedup.

See the [Kira sufficiency test](kira_sufficiency_test/README.md) for the equations, fixed protocol, raw symbolic remainders and independent checks.

<!-- kira-cost-comparison -->
The frozen model is also tested in [Kira_comparison](../Kira_comparison/README.md), both as a filter on the stored source pool and as native per-sector seed bounds. The comparison is complete and independently checked. The main experiment contains 792 trials in 19 family cases; the direct native seed-bound comparison contains 84 trials in seven independent-basis families. Against Kira with the full stored source pool, learned seeds have geometric mean complete-process/prepared-input time ratios 1.720/1.116, and learned rows have ratios 1.719/1.205. Learned native seed bounds have ratios 1.596/1.344 against default native bounds and 1.671/1.373 against restricted native bounds. Against the control with seed bounds taken directly from target indices, the native learned ratios are 1.425/1.141. Ratios use matched case medians from three repeats; values below one indicate lower time. Complete-process time includes loading, inference, exact algebra, fallback and coefficient checks. Prepared-input time excludes family and model loading. Completion counts, all resource outcomes, individual cases and operation measures appear in summary.json and native_seed/summary.json. The direct native test learns sector envelopes. The row model still acts on fixed source identities and changing target rows.

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

<!-- responsive-fermat-exit -->
The responsive Fermat shutdown comparison contains 480 planned records, 416 measured trials and 400 exact completions in twelve new held-out one-loop box instances. For one target, the modified learned workflow has a complete-time ratio of 0.384629 to the original learned workflow (descriptive 95% interval 0.342069–0.452551; 12 paired batches), with geometric mean times 5.528 and 2.126 seconds. For sixteen targets the corresponding ratio is 0.685856 (interval 0.540426–0.844099). Against the full pool with the same shutdown improvement, the single-target learned ratio is 0.690298 (interval 0.423691–0.931312). All completed reductions matched exact references. Both learned methods use the same original weights, threshold, early master check and fallback. The shutdown change preserves symbolic operations and also applies to the full-pool control. These measurements use existing IBP identity pools; they exclude their original generation.

Code, measurements, source patch, frozen inputs and independent checks are in Kira_comparison/fast_expression/. The report explains the separate shutdown and learned-seed effects in kira_fast_expression.tex and figures/responsive_exit_times.pdf.

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
