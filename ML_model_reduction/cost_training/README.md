# Row policies trained on measured algebraic cost

This folder contains the code and records for row policies trained on measured algebraic cost.

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
| [reduction_cost.patch](reduction_cost.patch) | This patch records changes to the native Kira source. |
| [reduction_tree.patch](reduction_tree.patch) | This patch records changes to the native Kira source. |
| [s00_cost_policy.h](s00_cost_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s01_build.py](s01_build.py) | Patches source selection inside native Kira and reuse the responsive shutdown. |
| [s02_build.sh](s02_build.sh) | Scheduler wrapper for build; its header sets the resource limits. |
| [s03_train.py](s03_train.py) | Fit a small cost ranker to exact counterfactual Kira updates. |
| [s04_predict.py](s04_predict.py) | Returns probabilities and the chosen native source-row candidate. |
| [s05_fit.sh](s05_fit.sh) | Scheduler wrapper for fit; its header sets the resource limits. |
| [s06_train_continuation.py](s06_train_continuation.py) | Train on measured remaining forward-elimination operations in exact Kira continuations. |
| [s07_fit_continuation.sh](s07_fit_continuation.sh) | Scheduler wrapper for fit continuation; its header sets the resource limits. |
| [s08_train_tree.py](s08_train_tree.py) | Fit a small nonlinear cost model from the same exact continuations. |
| [s09_fit_tree.sh](s09_fit_tree.sh) | Scheduler wrapper for fit tree; its header sets the resource limits. |
| [s10_tree_policy.h](s10_tree_policy.h) | Source-row cost policy for Kira; GPL-3.0-or-later. |
| [s11_build_tree.sh](s11_build_tree.sh) | Scheduler wrapper for build tree; its header sets the resource limits. |
| [s12_promote_tree.py](s12_promote_tree.py) | Preserves the linear continuation model and install the validated tree candidate. |

## Data and supporting files

- [COPYING](COPYING): License terms for the code in this folder.

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [feature_schema.json](feature_schema.json): Saved feature_schema.json record for row policies trained on measured algebraic cost; the producer code defines its fields.

- [trained_model.json](trained_model.json): This file contains a saved model or its description.

- [trained_weights.txt](trained_weights.txt): This file contains a saved model or its description.

- [training_results.json](training_results.json): This file records training progress or training inputs.

- [tree_build.json](tree_build.json): Saved tree_build.json record for row policies trained on measured algebraic cost; the producer code defines its fields.

- [tree_candidate_model.json](tree_candidate_model.json): This file contains a saved model or its description.

- [tree_candidate_results.json](tree_candidate_results.json): Saved tree_candidate_results.json record for row policies trained on measured algebraic cost; the producer code defines its fields.

- [tree_candidate_weights.txt](tree_candidate_weights.txt): This file contains a saved model or its description.

- [tree_promotion.json](tree_promotion.json): Saved tree_promotion.json record for row policies trained on measured algebraic cost; the producer code defines its fields.

## Child folders

- [immediate_cost_v1](immediate_cost_v1/README.md).

- [linear_continuation_v2](linear_continuation_v2/README.md).

- [model_test](model_test/README.md).
