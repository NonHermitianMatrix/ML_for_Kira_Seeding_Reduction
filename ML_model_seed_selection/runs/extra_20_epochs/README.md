# Superseded continuation

This historical continuation stopped after 19 completed passes and 70,000 targets in the next pass when the user requested twenty new passes on the expanded loop-order collection. Its latest saved weights and optimizer were preserved in ../before_all_loops_20/runs/latest.pt and initialize the expanded run. The current request authorizes publication of these historical records with the new models. Do not use this old launcher for the expanded-data phase; use ../../s15_run_all_loops.sh. The original workflow is recorded below.

# Twenty additional training epochs

This cluster-only continuation resumes the published ten-epoch weights and optimizer state and stops at thirty total epochs. It uses the same 693 training families, architecture, objective, learning rate and remaining settings. No held-out test is run and no Git command publishes the updates.

../epochs_10_snapshot/ preserves the original compact model, optimizer checkpoint, configuration and metadata. The existing model_test results and report describe that ten-epoch model. They do not measure the continued model.

request.json records the initial hashes, original settings and requested total. s00_continue.py verifies the starting model and optimizer and runs the continuation. s01_run.sh supplies scheduler and resource limits. jobs.json identifies each execution, scheduler.log records progress, and preflight.json records the checkpoint checks.

Run from the project root with:

    qsub ML_model_seed_selection/runs/extra_20_epochs/s01_run.sh

The job requests one CPU and 4 GiB, caps virtual memory at 3 GiB and any single output file at 128 MiB, and retains the existing project storage guard. If its bounded training time expires, it can submit a successor to continue from the last checkpoint, with at most three jobs for this request. Other failures stop explicitly.

The epoch goal overrides only the training schedule. The original configuration and data-preparation files remain unchanged. The active optimizer checkpoint is ../latest.pt and the compact model is ../../trained_model.pt. The compact model is replaced after epoch thirty. Training progress remains in ../training_status.json and ../training.jsonl.

Keep these weights, logs and metadata on Hoffman until the user requests publication. Report updates and testing require a separate instruction.
