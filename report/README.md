# Report copies

This folder contains the LaTeX sources, bibliography, build file and rendered PDF. The current copies must agree on Hoffman, GitHub and the local machine.

The local folder is /home/physics/projects/ML_for_Kira_SeedReduction/report. The Hoffman folder is /u/home/r/rushil/ML_for_Kira_Seeding_Reduction/report. GitHub stores the same folder on the main branch.

The local project is a shallow, partial Git checkout. Its sparse file selection includes report/, rules.md and .gitignore. Integral datasets and model-training files are not checked out or downloaded.

After report changes on Hoffman, rebuild the PDF and publish the sources and PDF together. The local helper .tools/report-sync/s02_sync_report.py accepts the reviewed commit and its report-file hash manifest. It fetches commit/tree metadata with the blob:none filter and applies a two-tree fast-forward checkout restricted to the existing sparse paths. It prefetches only the explicitly allowed report/rules and root Git attributes blobs and disables network access during checkout. This avoids downloading integral-data blobs or performing a content merge over them. The cache audit in s01_prune_git_cache.py verifies that only report, rules, .gitignore and root .gitattributes metadata blobs remain locally, while preserving Git history metadata.

The local Git connection uses the existing Hoffman SSH authentication and Hoffman's existing GitHub access. Its helper is .tools/report-sync/s00_git_via_hoffman.py, configured through core.sshCommand. No credentials are stored in this repository. The helper relays Git's SSH arguments through Hoffman. The connection requires network access to Hoffman.

Preserve local edits before pulling, and resolve any differences before declaring the report synchronized. Compare the report file hashes when checking the three copies. Git synchronization runs when requested or when the report is updated; no background synchronization service is installed.

The earlier local report and rules are retained in .tools/report-sync/before-link/ on the local machine.

<!-- expanded-report -->
The current report describes 17,100 family instances, 57,979 family-local master entries and 2,301,272 targets. The later additions contain 1,250 restricted coupled-vacuum mass profiles at each loop order from one through twelve, following the earlier 100 profiles at orders two through twelve. higher_loops.tex derives their master bases, exact identities, reverse target construction and grouped division.

seed_model.tex and reduction_model.tex describe the two models and their twenty new passes over 1,610,890 training targets. seed_model_test.tex and reduction_test.tex give the frozen results for 690,382 targets in 5137 held-out families. reduction_training.tex records the expanded-data reduction training. The fourteen current PDF plots are in figures/. Earlier checkpoints and tests remain in the model archives on Hoffman and GitHub.

The report distinguishes reference-set agreement from seed sufficiency, recorded next-action agreement from complete reductions, and sampled finite-field checks from symbolic reconstruction. The added family domain and shared lower-sector physics limit claims about generic high-loop integrals, unseen loop orders and full Kira speedups.

The bibliography links the expanded data and models to commit 0be1c2b3884bc736e22901a7e2304e3ba6d75497 and the tested outputs to commit 2ed8b26e977fa2dca5f464532ee9891712f7f417. Raw data, models and predictions remain on Hoffman and GitHub; only the complete report is synchronized locally.

The conclusion in report.tex brings together the master-based target construction, both frozen-model tests, the measured reduction cost and the limits of the tested family domains. It includes the symbolic master-span sufficiency test, native equation-generation comparisons and evolving-matrix cost measurements. The reported test data and model weights remain those of the cited releases.

seed_kira_test.tex describes all 690,382 reserved targets tested for exact membership in their master span with predicted, full and empty IBP seed sets through Kira's user-defined-system interface. Predicted sets suffice for 652,517 targets (94.515%). The full candidate pool suffices for 690,382. The associated results and code are fixed at 097204f4228b5999c4379c8da57db1aa9495c367; the new PDF figures are kira_seed_sufficiency.pdf and kira_seed_sets.pdf. These are exact symbolic membership tests within the stored source pools, with three independent finite-field rank checks. The full experiment does not reconstruct all rational master coefficients. This experiment does not measure native Kira seeding or a total solver speedup.

<!-- kira-cost-comparison -->
kira_comparison.tex reports the complete symbolic cost comparison: 792 main trials in 19 held-out families and 84 direct native seed-bound trials in seven independent-basis families. The same frozen models, targets and prescribed master bases are used throughout. The five new comparison figures show complete and prepared-input time, equation counts, memory, committed row operations and native seeding. Both fallback and incomplete trials remain in the accounting. The report distinguishes stored identities from native generation and target-row preprocessing from full Kira pivot selection. The fixed data release is 297d7dd0c134e9f873de36b818c8dd3377c9089c. The supplied abstract remains unchanged.

The rendered paper has been checked for readable plot labels, continuous result paragraphs, complete citations and preserved abstract text. Its conclusion distinguishes the full integral collection from the held-out test set and states the measured runtime increases.



<!-- live-matrix-comparison -->
kira_live_matrix.tex describes 84 repeated trials with the frozen row model inside Kira's symbolic forward elimination. It compares stock Kira, instrumented Kira, the deterministic schedule control and the learned policy on seven independent-basis families and 99 targets. The new time and operation figures are live_kira_times.pdf and live_kira_operations.pdf. The data release is d08fdcddcc64060a7f0ccd397fd3e0924b97c63a. All final reductions passed their exact checks. The supplied abstract is unchanged.

<!-- native-acceleration -->
kira_acceleration.tex and kira_acceleration_results.tex explain direct seed filtering, NumPy seed inference, the compiled source-row policy and their reserved native comparisons. The new plots are native_acceleration_times.pdf, native_acceleration_work.pdf and native_transfer_times.pdf. kira_adaptive_development.tex records the separate early-admission experiments, and kira_transfer_results.tex gives the two-loop transfer comparison. The numerical values come from Kira_comparison/acceleration/summary.json and its independent audit. The supplied abstract and earlier results remain unchanged. The complete report folder, including the new figures, is synchronized to Hoffman, GitHub and the local report directory.

<!-- whole-expression-confirmation -->
kira_expression_results.tex adds the complete-expression seed interface, its validation and its 360-record reserved confirmation. figures/whole_expression_times.pdf compares complete costs with the full equation pool and the fixed distance rule. The source values are expression_summary.json, expression_test_summary.json and their independent audits. The conclusion reports native, two-loop transfer and whole-expression results with their separate scopes.

<!-- matched-admission-confirmation -->
The additional matched-admission confirmation applies the same early master check and full-pool fallback to learned seeds and the 64-seed distance control. It contains 360 planned records, 348 measured trials and 345 exact completions. The learned complete-time ratios are 0.931643 (descriptive 95% interval 0.844721–1.030866; 23 complete paired batches) against the full pool and 0.925206 (descriptive 95% interval 0.847770–1.023721; 23 complete paired batches) against the matched distance control. The full-pool control completed 0 additional batches, and the learned method completed 0 additional batches. This repeats the same twelve physical family instances; it is not a new-family test. The first comparison is fully retained, and its distance control lacks the early admission check.

kira_expression_matched.tex and figures/whole_expression_matched_times.pdf give the matched-admission result. Both selectors use the same early check in this comparison.

<!-- single-target-result -->
The predefined single-target comparison gives 8.6% lower geometric mean complete time against the full-pool Kira control and 8.7% lower time against the distance control with the same early check. Both descriptive intervals lie below one across all twelve held-out instances, with five exact repeats per method. The earlier confirmation gave 7.8% lower time against the full pool for this batch size. The sixteen-target intervals include one. This measured benefit applies to one constructed target expression at a time using an existing IBP identity pool; it does not establish a native Kira or general high-loop speedup.

<!-- responsive-fermat-exit -->
The responsive Fermat shutdown comparison contains 480 planned records, 416 measured trials and 400 exact completions in twelve new held-out one-loop box instances. For one target, the modified learned workflow has a complete-time ratio of 0.384629 to the original learned workflow (descriptive 95% interval 0.342069–0.452551; 12 paired batches), with geometric mean times 5.528 and 2.126 seconds. For sixteen targets the corresponding ratio is 0.685856 (interval 0.540426–0.844099). Against the full pool with the same shutdown improvement, the single-target learned ratio is 0.690298 (interval 0.423691–0.931312). All completed reductions matched exact references. Both learned methods use the same original weights, threshold, early master check and fallback. The shutdown change preserves symbolic operations and also applies to the full-pool control. These measurements use existing IBP identity pools; they exclude their original generation.

Code, measurements, source patch, frozen inputs and independent checks are in Kira_comparison/fast_expression/. The report explains the separate shutdown and learned-seed effects in kira_fast_expression.tex and figures/responsive_exit_times.pdf.

<!-- integrated-native-runtime -->
The latest extension is in kira_integrated_methods.tex and kira_integrated_results.tex. It documents compiled unchanged seed inference, threshold fitting on complete native cost, sparse row features, trajectory-selected policies, bounded back substitution, model-free controls and explicit exported-basis admission. The frozen comparison contains 560 workflows in sixteen batches from eight new physical profiles. The new figures are integrated_runtime_times.pdf and integrated_runtime_operations.pdf. Data, models and exact checks are fixed at dca94891c24aae5b0602cc6794e4aa2e42921647. All earlier results and the exact supplied abstract remain preserved. The reported native baseline receives the same shared runtime improvements as the learned policies.


<!-- two-row-confirmation -->
kira_integrated_pair.tex gives the two-row scalar-multiple identity, the 144-workflow parity and timing validation, and the 400-workflow confirmation on the same eight profiles. All source choices and exact results remain unchanged. figures/integrated_pair_times.pdf separates complete time from forward-stage time. The additional inverse cache remains disabled. Eight basis-only application checks pass independent postrun coefficient comparisons; production use can supply master indices without target answers. The revised conclusion reports the latest measured model effects and their limits. The original abstract remains unchanged.




<!-- shared-evaluation -->
The latest section, kira_shared_evaluation.tex, documents reuse of affine prefixes in the unchanged seed network and unordered-pair cancellation estimates in the unchanged row policy. It reports 180 validation workflows, 800 paired implementation-confirmation workflows, all failed attempts and eight basis-only application checks. Figure shared_evaluation_times.pdf separates improvements over the preceding implementation from comparisons with the native control. The supplied abstract is unchanged. Frozen data commit: 387e80d58304bfd837ba942f6cba3d95a83daa7d.




<!-- parallel-inference -->
The latest section, kira_parallel_inference.tex, explains vector evaluation of independent neural outputs, exact Euclidean field inverses and direct integer features. It preserves 144 rejected-candidate validation workflows and reports 144 final validation workflows, 640 confirmation workflows, all fallback attempts and eight basis-only application checks. The new figure separates implementation costs from comparisons with native choices. The supplied abstract is unchanged. Data commit: a766f15379be2d777628c215e7b5c41016c95dec.

<!-- target-dependent-equation-selection -->
The equation_selection section introduces the third probability model and its native Kira integration. equation_selection_results and equation_selection_domain retain the broad test, including incomplete vacuum filters and their fallback costs. equation_selection_confirmation documents the restricted 21-target sunrise route and six fresh confirmation profiles. The new figures separate complete time, equation preparation and equation counts. Code, model weights, frozen protocols, exact checks and data are in [ML_model_equation_selection](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/63d87b1e863e9387eb821623ca09b1ae634884f7/ML_model_equation_selection). The supplied abstract remains unchanged.

The current equation-policy interface uses native seed and row choices in its measured sunrise domain. It disables equation filtering when an earlier learned policy is requested because the three-model composition was slower. The complete report-generation entry point is ML_model_equation_selection/s39_finish_report.sh.

Equation-selection data commit: 63d87b1e863e9387eb821623ca09b1ae634884f7.
