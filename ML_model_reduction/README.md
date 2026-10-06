# Reduction-propagation model

The model scores the supplied allowed source-row eliminations at the current target row, returns a probability for every action and selects the highest-scoring action with its estimated confidence. The exact solver performs the selected finite-field operation. It has 10,529 parameters and 132 input features per action.

The current checkpoint completed twenty new passes over 266,890 training targets from 1,463 complete families. Every loop order from one through twelve occurs in training. The fixed test division contains 114,382 targets from 637 families. New mass profiles remain in one split across all loop orders; earlier assignments are preserved. The higher-loop families are restricted coupled vacuum integrals. Both splits share some lower-sector physics and every loop order. Reference seed sets and paths are sufficient; their minimality is not proved.

s00_common.py, s01_state.py and s03_model.py define file guards, exact row features and the neural scorer. s02_prepare_data.py replays training traces and creates bounded state files. s10_train_all_loops.py continues the saved weights and optimizer for twenty expanded-data passes; s11_run_all_loops.sh runs preparation and training. s05_predict.py exposes prediction and optional exact row application. Earlier s04 and s06 through s09 scripts preserve the initial workflow.

trained_model.pt stores the current inference model; trained_model.json records measured training results. runs/all_loops_latest.pt retains the optimizer and exact resume position, and runs/all_loops_history.json records all twenty new passes. runs/before_all_loops_20/ preserves the preceding weights, optimizer, metadata and source. The saved lineage records the earlier dataset progress separately. validation.json and release_manifest.json verify the current model. data/ contains only encoded training examples, with source hashes and the held-out count recorded separately.

Training retains the prior thirty-epoch weights and AdamW state, learning rate 0.001, weight decay 0.0001, gradient norm limit one and state batch bounds. Only states with multiple allowed actions contribute ranking loss. The experiment changes one target row against fixed source identities; it does not benchmark a complete Kira elimination system.

The frozen expanded-data test is complete. model_test/archive_before_all_loops/ retains the previous tests and their exact source. Current tests and plots occupy model_test/; the report is updated from these checked records. Generated data, model files and tests stay on Hoffman and GitHub; the report also stays on the local machine. Jobs bound CPU use, virtual memory and output sizes, and enforce the combined 10 GB ceiling.
The training metadata records the state at training completion; release_manifest.json records the current publication and test stage.

Prediction uses s05_predict.py state.json --apply --output prediction.json with the existing .tools/seed-model/venv/bin/python after loading the Hoffman Python 3.9.6 module. The input gives prime, public family information, sparse rows, row_roles, master_columns and supplied actions. Each action contains id, source_row, destination_row and pivot_indices. The optional --apply flag performs the selected exact modular row update. Source rows must represent zero identities and pivots must be nonzero.

The 132 action features describe pivot indices, row support, candidate cancellations, immediate arithmetic and public family information. A sparse modular trial update supplies local counts for each action; future trajectories and recorded selected-action IDs do not enter predictive features. The interface accepts multiple destination rows, while current training uses one changing target row. Limits are sixteen indices, 10,000 rows, 10,000 actions, 250,000 matrix entries and 4,096 entries per row.

<!-- expanded-test-results -->
The frozen model was tested on all 114,382 targets in 637 held-out families. Recorded-action top-one agreement on choice states is 88.324263%; top-three agreement is 98.819872%. Averaging credit over highest-scoring ties gives 83.699677% agreement; the tied fraction is 11.184840%. The selected action gives the same next sampled row in 88.336112% of choice states. The learned policy matches all three sampled master expansions for 114,179 targets, and the local comparison rule does so for 113,703. Mean attempted reduction times are 10.162832 ms and 0.534528 ms, respectively.

The model changes one target row against fixed source identities. The local rule minimizes the next nonmaster count, total row support, immediate operation count and fixed equation-ID tie-break in that order. Three finite-field samples check complete paths. The test establishes neither global path minimality nor a full Kira runtime improvement.

See model_test/README.md for the complete frozen protocol and artifacts.
