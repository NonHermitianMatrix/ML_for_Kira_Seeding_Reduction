# Initial bounds and corrected measurements

The first probes and part of the first training collection used a positive-index bound below a declared top-level sector in some cases.
Kira rejected those inputs before reduction.
The corrected runner raises that bound before every attempt for all methods.

The files s00_study.py, s02_native.py, and s04_train_test.py preserve the initial sources.
The file protocol.json preserves the initial protocol.
The file revision.json lists the archived measurements and the number of unchanged records retained.
The archived training files never supply corrected training labels.
No reserved test had started when this correction was made.

See the [current study guide](../../README.md) for the scripts, inputs, outputs, dependencies, and execution order.
