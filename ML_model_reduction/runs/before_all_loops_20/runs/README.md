# Reduction-model training run

Training completed thirty epochs on the existing training states. The additional twenty epochs continued both weights and optimizer from epochs_10_snapshot/. latest.pt retains the current optimizer, history.json contains all thirty epochs, and status.json records training completion. extra_20_epochs/ records the continuation, and ../model_test/ evaluates the resulting frozen model.

The current test and report replace the ten-epoch evaluation. Original weights and optimizer checkpoints remain in epochs_10_snapshot/, while commit c2ba11c579c8851a22c69132e36a03f9ba4aa8b7 retains the previous tests and report. Training metadata with testing-deferred or published-false fields describe the state when training ended; the current evaluation and publication records document later steps.

The scheduler.log and report_build.log files in this directory record the initial training stage. Current evaluation and report-build logs are in ../model_test/.
