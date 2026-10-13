# Reserved scattering tests

Each compressed JSON file stores a complete measured workflow or a basis-only application check.
The measured methods are native Kira, the original equation tree, the new seed tree and the new equation tree.
Each of nine batches has five repetitions of all four methods.
Every workflow includes all fallback attempts.
The records retain exact coefficients, basis checks, elapsed times and equation counts.
Files ending in `application.json.gz` check a reduction without giving the driver target reference coefficients.

`summary.json` gives all 180 workflow checks and eighteen application checks.
It includes per-case median times, model-to-native ratios, fallback counts and three-group descriptive intervals.
All ratios include input preparation, prediction, algebra, checks, cleanup and retries.
Offline references, training and later record archiving remain outside the timer.

Use `s00_scattering_study.py test` to produce the tests after the settings are fixed.
Use `s02_analyze.py` to check the files and create the summary and paper figures.
Read [the study guide](../README.md) for the split rules and limitations.
