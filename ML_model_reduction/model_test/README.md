# Frozen expanded-data test

The frozen model was tested on all 114,382 targets in 637 held-out families. Recorded-action top-one agreement on choice states is 88.324263%; top-three agreement is 98.819872%. Averaging credit over highest-scoring ties gives 83.699677% agreement; the tied fraction is 11.184840%. The selected action gives the same next sampled row in 88.336112% of choice states. The learned policy matches all three sampled master expansions for 114,179 targets, and the local comparison rule does so for 113,703. Mean attempted reduction times are 10.162832 ms and 0.534528 ms, respectively.

families/ stores probability arrays and complete model/comparison paths. test_results.json, family_metrics.json, paired_comparison.json, tie_metrics.json and target_metrics.jsonl.gz provide measured results. s00_test_common.py and s01_policies.py define the fixed protocol; s02_evaluate.py runs it. s03_check_metrics.py checks metric formulas, s04_run_test.sh runs the bounded workflow, s05_validate_outputs.py independently replays saved paths and probabilities, s06_plot_results.py draws the six plots, s07_update_report.py renders the scientific sections, s09_validate_checkpoint.py checks the frozen twenty-pass weights, and s10_parallel_test.py runs four disjoint family groups on one compute node before aggregation.

figures/ contains six PDF plots and PNG previews. validation.json records independent checks. archive_before_all_loops/ retains the previous tests and their source.

Every loop order from one through twelve occurs in training and testing. Related new mass profiles stay within one split across loop orders. The new data use restricted coupled vacuum families, and different profiles can share lower-sector physics. Weights, split, threshold and confidence maps remain fixed during evaluation. The tests do not establish transfer to unseen loop orders.

The model changes one target row against fixed source identities. The local rule minimizes the next nonmaster count, total row support, immediate operation count and fixed equation-ID tie-break in that order. Three finite-field samples check complete paths. The test establishes neither global path minimality nor a full Kira runtime improvement.

Checkpoint SHA-256: 3e8e998cc12325e57ad180d704f6e0b7f4a2bacd9e35fe6c7eee94c055636998.
