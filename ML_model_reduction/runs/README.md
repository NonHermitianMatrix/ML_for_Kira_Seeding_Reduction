# Reduction-model run records

status.json gives preparation/training progress. history.json contains losses and reference-choice agreement recorded during parameter updates, not held-out accuracy. latest.pt resumes model and optimizer state at a completed group boundary.

scheduler.log records the completed preparation and training job. preparation_support_check.log records the initial audit that identified differences between symbolic and sampled support counts. The preparation code now retains this distinction while requiring exact sampled row replay.

example_state.json and example_prediction.json demonstrate inference on one training state. report_values.json supplies the counts used in the report, and report_build.log records the final artifact checks and PDF build. The final model is stored one directory above as trained_model.pt.

All run data stay on Hoffman and GitHub. Do not use these training measurements as test results.
