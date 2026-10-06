# Frozen expanded-data test

The frozen model was tested on all 114,382 targets in 637 held-out families. At the fixed threshold 0.5, pooled precision is 90.415884%, recall is 76.305208%, F1 is 82.763408%, and complete reference-set agreement is 56.831494%. Mean target average precision is 93.737419%.

predictions/ stores per-family probability arrays, labels and target IDs; prediction_manifest.json identifies their hashes. per_target_metrics.jsonl.gz, family_metrics.json, test_results.json and curves.json give the measurements. s01_evaluate.py performs frozen inference, s02_run_test.sh runs the bounded test, s03_plot_results.py draws the six plots, s04_validate_outputs.py independently checks counts and saved probabilities, and s06_update_report.py renders the scientific sections.

figures/ contains six PDF plots and PNG previews. validation.json records independent checks. archive_before_all_loops/ retains the previous tests and their source.

Every loop order from one through twelve occurs in training and testing. Related new mass profiles stay within one split across loop orders. The new data use restricted coupled vacuum families, and different profiles can share lower-sector physics. Weights, split, threshold and confidence maps remain fixed during evaluation. The tests do not establish transfer to unseen loop orders.

The labels identify one sufficient reference seed set. Alternative sufficient sets can differ, and this evaluation does not run Kira with the predicted sets or establish globally minimal seeds. Candidate-label accuracy must be read with the sparse positive-label fraction.

Checkpoint SHA-256: 9c73aa38ce869f5d70f4c8f5a0a4944d69e4c43e35a4c3451ecb31e9076294cc.
