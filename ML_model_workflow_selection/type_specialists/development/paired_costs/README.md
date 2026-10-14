# Paired training costs

The s10_pair_training.py script repeats batches with measurements from more than one worker.
The plan.json file lists those batches before repetition.
The initial_candidates.json and initial_freeze.json files preserve the earlier fit.
The training/ folder preserves the replaced measurements.
The completion.json file records the final fit and within-batch worker checks.
No reserved test enters this refit.
See the [study guide](../../README.md) for inputs, outputs, dependencies, and script order.
