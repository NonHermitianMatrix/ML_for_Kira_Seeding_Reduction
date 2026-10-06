# Historical continuation on the earlier dataset

This directory records the completed continuation to thirty passes before the expanded loop-order phase. The current model uses twenty further passes over the expanded dataset; see ../README.md and ../../README.md.

# Twenty additional training epochs

This continuation resumes the published ten-epoch weights and optimizer state and stops at thirty total epochs. It uses the same 693 training families, architecture, objective, learning rate and remaining settings. No held-out test is run and no Git command publishes the updates.

../epochs_10_snapshot/ preserves the original compact model, optimizer checkpoint, configuration and metadata. Commit c2ba11c579c8851a22c69132e36a03f9ba4aa8b7 retains the ten-epoch test and report. The current model_test/ evaluates the thirty-epoch model under a later user instruction.

request.json records the initial hashes, original settings and requested total. s00_continue.py verifies the starting model and optimizer and runs the continuation. s01_run.sh supplies scheduler and resource limits. jobs.json identifies each execution, scheduler.log records progress, and preflight.json records the checkpoint checks.

Run from the project root with:

    qsub ML_model_reduction/runs/extra_20_epochs/s01_run.sh

The job requests one CPU and 4 GiB, caps virtual memory at 3 GiB and any single output file at 128 MiB, and retains the existing project storage guard. If its bounded training time expires, it can submit a successor to continue from the last checkpoint, with at most three jobs for this request. Other failures stop explicitly.

The epoch goal overrides only the training schedule. The original configuration and data-preparation files remain unchanged. The active optimizer checkpoint is ../latest.pt and the compact model is ../../trained_model.pt. The compact model is replaced after epoch thirty. Training progress remains in ../status.json and ../history.json.

The user subsequently authorized testing, report updates and GitHub publication for this reduction model. The separate seed-model continuation remains on Hoffman.
