# Joint reduction of two target requests

This test joins two disjoint target lists from the same integral family and kinematics.
It compares separate native reductions, joint native reduction, integrated joint reduction, and learned joint reduction.
The model stays frozen. The groups share reserved points with the main test.
Each method has five timing repetitions. Every result receives exact coefficient checks.
The complete timer includes grouping, prediction, fallback, and separating the returned coefficients.
Reference discovery remains outside this timer.

Run `s09_batching.py` from the parent folder through `s01_job.sh`.
`cases.json` defines the requests before the tests. Gzip files contain full results and solver attempts.
`summary.json` contains ratios and descriptive intervals over graph groups.
Read [the parent guide](../README.md) for dependencies and resource limits.

All 200 comparisons pass exact checks.
The standard joint ratio is 0.517474 relative to two separate native requests.
Its descriptive interval is [0.507293, 0.534572].
The learned-to-joint-integrated ratio is 0.995542, with interval [0.980961, 1.005803].
The native shared calculation supplies the main saving.
The [standard application](../s16_reduce_best.py) keeps the best fixed training strategy.
The model remains an optional comparison.
