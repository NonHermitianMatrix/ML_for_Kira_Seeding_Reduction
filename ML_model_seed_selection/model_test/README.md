# Frozen expanded-data test

The frozen model was tested on all 690,382 targets in 5137 held-out families. At the fixed threshold 0.5, pooled precision is 95.750448%, recall is 96.892412%, F1 is 96.318045%, and complete reference-set agreement is 84.332297%. Mean target average precision is 99.090018%.

predictions/ stores per-family probability arrays, labels and target IDs; prediction_manifest.json identifies their hashes. per_target_metrics.jsonl.gz, family_metrics.json, test_results.json and curves.json give the measurements. s01_evaluate.py performs frozen inference, s02_run_test.sh runs the bounded test, s03_plot_results.py draws the six plots, s04_validate_outputs.py independently checks counts and saved probabilities, and s06_update_report.py renders the scientific sections. The completed inference arrays and original timings were reused after replacing an obsolete storage cutoff with allocated bytes plus a 200 MB local allowance below 9.7 GB. Frozen inference and metric calculations remained unchanged. The cached evaluation and independent checks use pod_smp.q after a slow filesystem scan in the preceding allocation. original_inference_allocation.json identifies the original one-thread inference allocation for the retained timing arrays.

figures/ contains six PDF plots and PNG previews. validation.json records independent checks. archive_before_expansion_250/ retains the preceding tests and their source.

Every loop order from one through twelve occurs in training and testing. Related new mass profiles stay within one split across loop orders. The new data use restricted coupled vacuum families, and different profiles can share lower-sector physics. Weights, split, threshold and confidence maps remain fixed during evaluation. The tests do not establish transfer to unseen loop orders.

The labels identify one sufficient reference seed set. Alternative sufficient sets can differ, and this evaluation does not run Kira with the predicted sets or establish globally minimal seeds. Candidate-label accuracy must be read with the sparse positive-label fraction.

Checkpoint SHA-256: b8fb9cc088bd4e0cbbe1168d1e5fbd733ebea361fd41d3de48827672732ed977.

<!-- exact-kira-sufficiency -->
The exact Kira sufficiency test is complete for 690,382 reserved targets in 5,137 families. Predicted seeds suffice for 652,517 targets (94.515%). The full candidate pool suffices for 690,382 (100.000%), and background identities without IBP seeds suffice for 26,915 (3.899%). All symbolic decisions agree with three independent finite-field row-space checks. The model and threshold remain unchanged. This test checks existence of a reduction within the stored identity pools; it does not reconstruct all master coefficients or measure a native Kira speedup.

See the [Kira sufficiency test](../kira_sufficiency_test/README.md) for the equations, fixed protocol, raw symbolic remainders and independent checks.
