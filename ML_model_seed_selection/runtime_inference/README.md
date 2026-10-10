# Seed inference for complete native reductions

This folder reuses the original trained neural checkpoint and supplies two equivalent feature/inference interfaces. s00_vector_seed.py computes unchanged features with bounded NumPy arrays. s02_seed_runtime.cpp and s04_compiled_seed.py implement the same float32 network through a small compiled library. compiled_export.json records the source checkpoint/configuration and compiled_weights.bin contains the exported parameters. No reserved examples retrain these weights.

parity.json records bitwise vector-feature and probability agreement. compiled_parity.json and compiled_threshold_parity.json check probability tolerance and identical seed masks on thirty-six development contexts. cold_benchmark.json includes imports, loading and inference in forty-eight fresh-process checks. The compiled arithmetic is slower when warm; reduced startup cost motivates its production use.

threshold_policy.json fits execution thresholds from ninety-six complete training workflows, including failed subsets and native fallback. It preserves the earlier classification test's threshold. The allowed execution thresholds are 0.003, 0.01, 0.03, 0.1, 0.3 and 0.5. Unknown classes use the frozen transfer threshold for explicit model tests. Auto deployment separately retains native execution for unvalidated classes.

The native candidate region is finite. Coverage retains target seeds, the prescribed masters, sector corners and the specified first neighbours. The model does not enumerate all integer seed indices. Full costs and independent physical tests are in Kira_comparison/integrated_runtime/. That folder's resource cap also covers these files.

## Script order

- s00_vector_seed.py: Construct unchanged seed index features with bounded NumPy arrays.
- s01_verify.py: Check bitwise feature, embedding, probability and seed-decision parity.
- s02_seed_runtime.cpp: Bounded inference for the existing float32 seed network.
- s03_export_compiled.py: Export unchanged float32 weights into a bounded portable runtime archive.
- s04_compiled_seed.py: Apply the unchanged neural seed model without NumPy startup in production.
- s05_verify_compiled.py: Compare compiled neural inference with the unchanged NumPy network.
- s06_build_compiled.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s03_export_compiled.py; .tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s05_verify_compiled.py
- s07_cold_component.py: Measure a fresh-process seed decision, including imports and model loading.
- s08_cold_benchmark.py: Compare cold seed backends with identical candidates and decisions.
- s09_cold_benchmark.sh: Scheduler/build wrapper: .tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s05_verify_compiled.py --expanded; .tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s08_cold_benchmark.py
- s10_fit_thresholds.py: Fit execution thresholds from complete native training-workflow cost.

<!-- shared-evaluation-current -->
The preceding backend is s11_shared_runtime.cpp with s12_shared_seed.py and the original compiled_weights.bin. s89_build_shared.sh in the integration folder builds it. Shared affine prefixes preserve the floating-point addition order and give bitwise-identical probabilities in every checked context. The new library stays outside Git; the implementation and unchanged weight export are retained. See fast_evaluation/ for complete timing, exact parity, the freeze and current production entry.

<!-- parallel-inference-current -->
The latest backend is s13_lane_runtime.cpp with s14_lane_seed.py. It transposes weight storage once at loading and computes independent neural outputs together, preserving each float32 addition order. s109_build_parallel.sh compiles it without fused multiply-add or fast-math. All 36 development contexts and complete paired reductions retain identical probabilities and masks. The existing compiled_weights.bin and thresholds remain unchanged. See Kira_comparison/parallel_inference/ for costs, exact checks and the current entry.
