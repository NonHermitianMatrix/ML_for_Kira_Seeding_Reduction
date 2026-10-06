# Seed-model training run

Training completed all ten passes through 168,330 training targets. The run made 210420 optimizer updates. No held-out model testing was performed during training. The later authorized test is documented in ../model_test/README.md.

../trained_model.pt contains the final model, and latest.pt also retains optimizer state. training.jsonl records each completed epoch. training_status.json gives the final status, input_checks.json records the training-only input checks, and scheduler.log contains the job output. The model fingerprint and training source provenance are in ../trained_model.json.
