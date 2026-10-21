# Row policies trained on complete runtime

This folder contains the code and records for row policies trained on complete runtime.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Scripts

| File | Purpose |
|---|---|
| [s00_runtime_policy.h](s00_runtime_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s01_modular_features.h](s01_modular_features.h) | Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later. |
| [s02_modular_policy.h](s02_modular_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s03_test_features.cpp](s03_test_features.cpp) | Standalone verification harness for modular coefficient features. |
| [s04_test_features.py](s04_test_features.py) | Verify modular values and row-cancellation estimates against exact SymPy arithmetic. |
| [s05_train.py](s05_train.py) | Fit compact row-cost trees with grouped validation and exact native cost labels. |
| [s06_fast_features.h](s06_fast_features.h) | Included inside namespace kira_cost, after Features and modular estimates exist. |
| [s07_fast_policy.h](s07_fast_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s08_policy_candidates.py](s08_policy_candidates.py) | Initializes bounded policy families for optimization on full native trajectories. |
| [s09_select_trajectory.py](s09_select_trajectory.py) | Ranks learned row policies by complete training trajectories, keeping validation separate. |
| [s10_sparse_policy.h](s10_sparse_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s11_final_policy.h](s11_final_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s12_cached_modular.h](s12_cached_modular.h) | Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later. |
| [s13_cached_policy.h](s13_cached_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s14_pair_policy.h](s14_pair_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s15_shared_modular.h](s15_shared_modular.h) | Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later. |
| [s16_shared_policy.h](s16_shared_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s17_euclid_modular.h](s17_euclid_modular.h) | Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later. |
| [s18_euclid_policy.h](s18_euclid_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s19_literal_modular.h](s19_literal_modular.h) | Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later. |
| [s20_literal_policy.h](s20_literal_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |

## Data and supporting files

- [feature_tests.json](feature_tests.json): Saved feature_tests.json record for row policies trained on complete runtime; the producer code defines its fields.

- [training_results.json](training_results.json): This file records training progress or training inputs.

- [trajectory_candidates.json](trajectory_candidates.json): This file records successive reduction states and checks.

- [trajectory_selection.json](trajectory_selection.json): This file records successive reduction states and checks.

## Child folders

- [candidates](candidates/README.md).

- [trajectory_candidates](trajectory_candidates/README.md).
