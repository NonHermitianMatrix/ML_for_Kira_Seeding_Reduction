# Elimination-model results for one family

The directory name identifies the tested integral family. These records evaluate the frozen row model on its recorded target states and reference paths.

- [predictions.npz](predictions.npz): NumPy arrays of model predictions.
- [summary.json](summary.json): result counts and summary measurements.
- [trajectories.jsonl.gz](trajectories.jsonl.gz): successive states, selected operations, and completion checks, one JSON record per line.

[The test guide](../../README.md) defines the model, producer scripts, and checks for this collection. Match target and action identifiers when comparing predictions with trajectories. A recorded path does not establish a globally fastest reduction. Native Kira timing is a separate test.
