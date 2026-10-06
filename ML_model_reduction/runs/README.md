# Reduction-model training runs

The current phase completed twenty complete passes over the expanded training choice states from 266,890 targets in 1,463 families. all_loops_latest.pt stores the model, optimizer, random state and resume position. all_loops_history.json records completed passes; status.json records preparation or training progress; all_loops_scheduler.log records the compute job. The final compact model is stored in ../trained_model.pt.

before_all_loops_20/ preserves the preceding thirty-pass model and optimizer used to start this phase. Those thirty passes used the smaller dataset. The twenty new passes use every represented loop order from one through twelve, with a separate epoch counter and preserved optimizer lineage.

latest.pt, history.json, scheduler.log, extra_20_epochs/ and epochs_10_snapshot/ retain earlier phases. Use all_loops_latest.pt for the expanded-data resume. The active trainer verifies the current preparation manifest, configuration and source hashes before resuming.

Only choice states contribute ranking loss. Forced states remain in the exact replay checks and have action probability one. Training reads no held-out labels. Current frozen tests and plots occupy ../model_test/, and its archive_before_all_loops/ folder preserves the preceding evaluation.
