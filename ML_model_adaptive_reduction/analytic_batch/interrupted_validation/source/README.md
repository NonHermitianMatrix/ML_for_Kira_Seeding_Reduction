# Source

Runtime and measurement sources for the preserved trials. The changed validation driver is omitted from this snapshot. Its initial profile was 3037. Use the parent scripts for the completed comparison at profile 3041.

Read [the study guide](../../README.md) for execution, controls, and limits.

## Additional scripts

- [s00_batch_common.py](s00_batch_common.py): Bounded study utilities and the unchanged preceding application.
- [s01_triangle.py](s01_triangle.py): Exact one-scale massless triangles, including integer numerator powers.
- [s02_batch_runtime.py](s02_batch_runtime.py): Select shared native reductions after exact analytic simplification.
- [s03_cases.py](s03_cases.py): Disjoint target batches and exact triangle checks.
- [s04_measure.py](s04_measure.py): Independent native references and fresh-process timing.
- [s05_collect.py](s05_collect.py): Collect complete reduction costs before selecting any new policy.
- [s07_train.py](s07_train.py): Train cost-sensitive trees on complete fresh-process reduction times.
- [s09_pipeline.py](s09_pipeline.py): Run dependent training stages only after their required checks pass.
