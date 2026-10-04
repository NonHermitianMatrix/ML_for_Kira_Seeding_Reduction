# Seed-model training run

Hoffman job 15036272 is running ten training epochs. launch.json records its resources, paths and launch details. Training uses only the 693 training families. No held-out model testing is included.

latest.pt contains the latest resumable checkpoint, including the optimizer state. training_status.json records progress, and training.jsonl records completed epochs. input_checks.json records checks on training inputs, and scheduler.log contains job output. The first saved checkpoint covered 1,000 targets and 125 optimizer updates.

Hoffman files update during training. GitHub contains the last published snapshot until the launcher publishes the final artifacts. After ten epochs, ../trained_model.pt will contain the final model and ../trained_model.json will record its counts and fingerprint. The completion step updates this README and publishes the model to GitHub. Testing requires a later user instruction.
