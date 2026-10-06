# Seed-selection model test

The completed test evaluates the frozen trained_model.pt on all 72,142 held-out targets from 307 families. The model receives public target, family, master-basis and candidate-seed information. Recorded sufficient seed sets enter the comparison only. The test keeps the trained parameters and the 0.5 threshold fixed, performs no optimizer updates and does not call Kira.

The test covers 33,828,275 candidate labels, including 201,885 recorded seeds. Pooled candidate accuracy is 99.940%, precision is 95.734%, recall is 94.112% and F1 is 94.916%. Assigning zero to every candidate would give 99.403% accuracy and zero recall. The predicted set exactly matches the reference for 81.916% of targets. The twenty highest-ranked candidates contain the full reference set for 99.831% of targets with nonempty reference sets.

Most test targets belong to one-loop families. The sole two-loop family has 144 targets and gives 11.290% precision, 41.553% recall and no exact reference-set matches at the fixed threshold. These results do not establish general high-loop performance. Agreement refers to one recorded sufficient seed set; alternative valid seeds can receive reference label zero. No minimal-seed, exact-reduction or Kira-speedup result is claimed.

The six [figures](figures/) cover training loss, candidate classifications, pooled precision and recall, ranked reference-seed recovery, confidence calibration and family variation. Each figure is available as PDF and PNG. Matching PDF figures are included in report/figures/ and the rendered report.

test_results.json contains pooled counts and metrics, equal-target averages, equal-family averages, groups by target kind and loop count, timing and provenance. family_metrics.json and family_metrics.csv contain all 307 family results. per_target_metrics.jsonl.gz contains one row per target. Denominators are recorded explicitly: recall and average precision exclude the two empty-reference targets; target precision excludes targets with no selected seed. Exact-set agreement includes every target.

predictions/ contains one compressed NPZ file per family. Each file stores float32 probabilities, uint8 reference labels, exact target IDs and kinds, integer seed vectors, binary cross-entropy and timing arrays. The row order follows target_ids, and each probability column corresponds to the matching seeds row. Labels are present for reproducible comparison only. The archives store the model and split SHA256 identifiers. prediction_manifest.json gives archive hashes and counts. Load these arrays with numpy.load(path, allow_pickle=False).

curves.json contains the score histograms and calibration summaries. The pooled precision-recall curve uses 4,096 bins and therefore approximates the full threshold curve. The confusion counts at 0.5 and target-level average precision use exact probabilities. Average precision groups tied scores; finite-k selections resolve ties by lexicographic seed indices. Confidence compares the returned class probability with observed reference-label agreement separately for labels zero and one. The test does not select a new threshold or fit a calibration transform.

s00_metrics.py defines the metrics, bounded curve accumulation and analytical metric checks. s01_evaluate.py verifies the saved model and split hashes, reads only held-out examples, evaluates them and saves results. It can reuse complete per-family prediction archives after an interruption when their model and split hashes match. s02_run_test.sh runs this evaluation on one Hoffman CPU with 4 GiB requested memory and a 3 GiB address-space limit.

s03_plot_results.py creates the six figures and their CSV data without rerunning the model. s04_validate_outputs.py independently recomputes every confusion count from the stored probabilities, checks target coverage and archive hashes, verifies that the model remains unchanged and compares the report figure copies. s05_make_figures.sh runs plotting and validation with the same bounded resources. s06_update_report.py fills report_section_template.tex from the completed results and writes report/seed_model_test.tex. s07_build_report.sh renders the updated report.

Run from the repository root:

    qsub ML_model_seed_selection/model_test/s02_run_test.sh
    # After evaluation finishes:
    qsub ML_model_seed_selection/model_test/s05_make_figures.sh
    python3 ML_model_seed_selection/model_test/s06_update_report.py
    qsub ML_model_seed_selection/model_test/s07_build_report.sh

The evaluation job was 15039780 and the figure/validation job was 15039804. metric_checks.json records analytical boundary cases; validation.json records the independent archive checks. test_status.json gives completion status. Logs remain in this folder. The metric and inference scripts record their hashes; the trained model SHA256 is 931ec67c287af4edbea3e6525e2cc1f8a95e04f164c24d262855986e44c3f589.

The full predictions and test records stay on Hoffman and GitHub. Only the report and its figure copies are synchronized to the local machine. The completed test reports reference-set agreement on the fixed family-grouped split.
