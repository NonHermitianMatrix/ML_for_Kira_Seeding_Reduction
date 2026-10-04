# Seed-model training run

Training is configured for ten epochs on 168,330 targets. training_status.json records live progress, training.jsonl records completed epochs, latest.pt is the resumable checkpoint, and scheduler.log is the Hoffman job output. The final model will be saved as ../trained_model.pt after all ten epochs.

The input checks use training examples only. Held-out model testing is deferred. The launcher updates this README and saves final metadata when training completes.
