# Row policies trained on native Kira cost

This folder contains separate lightweight row policies and preserves the earlier neural model and cost tree in their original directories. Native collection samples 2520 training and 1372 validation groups from six training and three validation physical profiles, with ordinary/deeper batches kept together. Twenty-four features include bounded modular estimates of symbolic cancellation. Modular values are heuristic features; exact Kira arithmetic and final coefficient checks determine accepted reductions.

s05_train.py fits immediate-time, coefficient-length and hybrid trees. s08_policy_candidates.py defines eighteen bounded linear candidates, and s09_select_trajectory.py ranks their full native training trajectories by committed forward operations. The trajectory_candidates/ folders hold each saved weight vector. trajectory_selection.json retains the training ranking and lineage. Subsequent validation chooses the final topology-specific policy; Kira_comparison/integrated_runtime/deployment.json is authoritative. Final test results never select weights.

s14_pair_policy.h applies the selected source inside Kira's current same-leading-integral row group. It computes only the features used by the sparse score, bounds modular parsing/caching and retains native behavior outside the supported group bounds. Its deterministic cancellation control receives the same optimization. In a two-row group, the alternative updates differ by a nonzero scalar, so cancellation features agree; the sparse score can sometimes retain the native source without computing those features. pair_summary.json records 144 validation workflows and 72 exact parity pairs: decision time ratio 0.344835 and forward time ratio 0.955232 compare the same learned policy with the shortcut disabled. The subsequent 400-workflow confirmation preserves the weights and decisions. These implementation ratios do not compare ML with native Kira. The additional modular-inverse cache failed its forward-stage adoption criterion and remains disabled. Choice traces include the selected source and normalized score confidence when tracing is enabled. Production timing disables detailed traces and retains aggregate operations and stage times.

Feature tests, full/shared-feature parity and sparse/full-policy parity remain preserved. Complete costs, references, all failed attempts, independent export checks and the comparison report reside in Kira_comparison/integrated_runtime/. The operation proxy excludes internal polynomial arithmetic and back substitution. Any speedup claim must use complete measured costs and the stated domain. The shared retained-data and memory caps apply.

## Script order

- s00_runtime_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
- s01_modular_features.h: Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.
- s02_modular_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
- s03_test_features.cpp: Standalone verification harness for modular coefficient features.
- s04_test_features.py: Verify modular values and row-cancellation estimates against exact SymPy arithmetic.
- s05_train.py: Fit compact row-cost trees with grouped validation and exact native cost labels.
- s06_fast_features.h: Included inside namespace kira_cost, after Features and modular estimates exist.
- s07_fast_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
- s08_policy_candidates.py: Initialize bounded policy families for optimization on full native trajectories.
- s09_select_trajectory.py: Rank learned row policies by complete training trajectories, keeping validation separate.
- s10_sparse_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
- s11_final_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
- s12_cached_modular.h: Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.
- s13_cached_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
- s14_pair_policy.h: Source-row cost policy for Kira; GPL-3.0-or-later.
