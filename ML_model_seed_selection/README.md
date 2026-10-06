# Seed-selection model

The model gives each supplied candidate seed a separate reference-membership probability, a binary label at p>=0.5 and the probability of the returned label. Several seeds can receive label one. It uses the symbolic target terms, every ordered pair of distinct terms, public family information and the chosen master indices. It has 28,097 parameters.

The current checkpoint completed twenty new passes over 266,890 training targets from 1,463 complete families. Every loop order from one through twelve occurs in training. The fixed test division contains 114,382 targets from 637 families. New mass profiles remain in one split across all loop orders; earlier assignments are preserved. The higher-loop families are restricted coupled vacuum integrals. Both splits share some lower-sector physics and every loop order. Reference seed sets and paths are sufficient; their minimality is not proved.

The active sequence is s12_prepare_features.py (training-only encoded features), s13_batch.py (masked batch calculation and comparisons with the original score function), s14_train_all_loops.py (twenty-pass continuation), s15_run_all_loops.sh (bounded scheduler wrapper), s16_validate_all_loops.py (checkpoint and source validation), s17_run_batch_pilot.sh (bounded execution pilot), and s18_validate_mixed_batches.py with s19_run_batch_validation.sh (mixed-target score and derivative comparisons). Earlier scripts s00 through s11 preserve the initial preparation and training workflow.

trained_model.pt stores the current inference model; trained_model.json records measured training results. runs/all_loops_latest.pt retains the optimizer and exact resume position, and runs/all_loops_history.json records all twenty new passes. runs/before_all_loops_20/ preserves the preceding weights, optimizer, metadata and source. The saved lineage records the earlier dataset progress separately. validation.json and release_manifest.json verify the current model. data/ contains only encoded training examples, with source hashes and the held-out count recorded separately.

The new phase uses batches of 32 targets. Factoring the first score layer avoids repeated target-context matrix multiplications without changing the network function. Direct comparisons with the original interface verify scores, loss and gradients. AdamW retains the previous optimizer state, learning rate 0.001 and weight decay 0.0001; the gradient norm is bounded by one. Scores describe membership in one reference seed set, and this model test alone does not run Kira with the predicted sets.

The frozen expanded-data test is complete. model_test/archive_before_all_loops/ retains the previous tests and their exact source. Current tests and plots occupy model_test/; the report is updated from these checked records. Generated data, model files and tests stay on Hoffman and GitHub; the report also stays on the local machine. Jobs bound CPU use, virtual memory and output sizes, and enforce the combined 10 GB ceiling.
The training metadata records the state at training completion; release_manifest.json records the current publication and test stage.

Prediction uses s04_predict.py --checkpoint ML_model_seed_selection/trained_model.pt --target FAMILY:ID, with an optional --seeds file containing an indices list. Run it with the existing .tools/seed-model/venv/bin/python after loading the Hoffman Python 3.9.6 module. The output includes predicted_label, probability_1, probability_0 and confidence for every candidate, ranked by probability_1. The public prediction path reads no reference labels.

The shared network uses 32-component hidden descriptions and a 64-component score layer with tanh activations. It compresses symbolic coefficient tokens into 64 signed hash components, which permits collisions. Ordered combinations mean all ordered pairs of distinct stored terms. Inputs accept at most sixteen indices, 512 terms and 10,000 supplied candidates. The candidate list is a bounded pool, and the chosen master basis is public input. Family IDs, split labels, reference coefficients, construction histories and future operation counts do not enter the scores.

<!-- expanded-test-results -->
The frozen model was tested on all 114,382 targets in 637 held-out families. At the fixed threshold 0.5, pooled precision is 90.415884%, recall is 76.305208%, F1 is 82.763408%, and complete reference-set agreement is 56.831494%. Mean target average precision is 93.737419%.

The labels identify one sufficient reference seed set. Alternative sufficient sets can differ, and this evaluation does not run Kira with the predicted sets or establish globally minimal seeds. Candidate-label accuracy must be read with the sparse positive-label fraction.

See model_test/README.md for the complete frozen protocol and artifacts.
