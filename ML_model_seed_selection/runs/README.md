# Expansion in progress

The next phase adds 250 mass profiles at every loop order from one through twelve, preserves all previous assignments, and will train twenty additional full passes. The previous completed model and optimizer remain in runs/before_expansion_250/. Active trained_model.pt and model_test results still belong to the preceding release until their replacements pass validation. No new training or testing has completed yet.

# Seed-model training runs

The current phase completed twenty complete passes over 266,890 targets from 1,463 training families spanning loop orders one through twelve. all_loops_latest.pt holds its model, optimizer, random state and resume position. all_loops_history.json records completed passes, training_status.json records current progress, and all_loops_scheduler.log records the compute job. The compact inference model is stored in ../trained_model.pt.

before_all_loops_20/ preserves the exact preceding snapshot used to start this phase. Its lineage records nineteen completed passes on the smaller dataset and 70,000 targets in the next pass. The previous continuation's later files remain separately preserved in this directory and extra_20_epochs/. The current phase uses its own epoch and update counters.

batch_equivalence.json records comparisons of batched scores, losses and gradients with the original prediction interface. batch_pilot.json records the bounded execution pilot. Neither uses held-out labels. The expanded training uses only ../data/ and its fixed manifest.

latest.pt, training.jsonl, scheduler.log and the older snapshots describe earlier training phases. Use all_loops_latest.pt for the current expanded-data resume. The active trainer verifies configuration, data and source hashes before it resumes. Current frozen tests and plots occupy ../model_test/, with earlier tests archived there.

s18_validate_mixed_batches.py, run with s19_run_batch_validation.sh, compares batched and individual scores, losses and gradients on training batches containing both one-term and multi-term targets. Its result is mixed_batch_validation.json. It reads a checkpoint snapshot in memory and performs no optimizer update.

The initial sample-selection log, mixed_batch_initial_selection.log, records a setup attempt whose selected family lacked both target types. The final mixed_batch_validation.json uses suitable training families and passed. Neither attempt updated model weights.

The first expanded-data allocation reached its original three-hour scheduler wall-time limit during pass twenty. all_loops_first_allocation.txt records the scheduler reason. The unchanged trainer resumes the saved weights, optimizer, random state and partial pass in a one-hour allocation. scheduler_resume.json records the checkpoint and allocation lineage; all_loops_resume_scheduler.log records the continuation. The completed history still covers exactly twenty full passes.

For a resumed allocation, s15_run_all_loops.sh skips feature regeneration when the checkpoint exists. The trainer checks the original feature manifest and source fingerprints before continuing, which preserves the training inputs and saved position.
