# Prediction cost within native seed selection

This folder contains the code and records for prediction cost within native seed selection.

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
| [s00_vector_seed.py](s00_vector_seed.py) | Constructs unchanged seed index features with bounded NumPy arrays. |
| [s01_verify.py](s01_verify.py) | Check bitwise feature, embedding, probability and seed-decision parity. |
| [s02_seed_runtime.cpp](s02_seed_runtime.cpp) | Bounded inference for the existing float32 seed network. |
| [s03_export_compiled.py](s03_export_compiled.py) | Export unchanged float32 weights into a bounded portable runtime archive. |
| [s04_compiled_seed.py](s04_compiled_seed.py) | Applies the unchanged neural seed model without NumPy startup in production. |
| [s05_verify_compiled.py](s05_verify_compiled.py) | Compare compiled neural inference with the unchanged NumPy network. |
| [s06_build_compiled.sh](s06_build_compiled.sh) | Scheduler wrapper for build compiled; its header sets the resource limits. |
| [s07_cold_component.py](s07_cold_component.py) | Measures a fresh-process seed decision, including imports and model loading. |
| [s08_cold_benchmark.py](s08_cold_benchmark.py) | Compare cold seed backends with identical candidates and decisions. |
| [s09_cold_benchmark.sh](s09_cold_benchmark.sh) | Scheduler wrapper for cold benchmark; its header sets the resource limits. |
| [s10_fit_thresholds.py](s10_fit_thresholds.py) | Fit execution thresholds from complete native training-workflow cost. |
| [s11_shared_runtime.cpp](s11_shared_runtime.cpp) | Bounded inference for the existing float32 seed network. |
| [s12_shared_seed.py](s12_shared_seed.py) | Applies the unchanged neural seed model without NumPy startup in production. |
| [s13_lane_runtime.cpp](s13_lane_runtime.cpp) | Bounded inference for the existing float32 seed network. |
| [s14_lane_seed.py](s14_lane_seed.py) | Applies the unchanged neural seed model without NumPy startup in production. |

## Data and supporting files

- [cold_benchmark.json](cold_benchmark.json): Saved cold_benchmark.json record for prediction cost within native seed selection; the producer code defines its fields.

- [compiled_export.json](compiled_export.json): Saved compiled_export.json record for prediction cost within native seed selection; the producer code defines its fields.

- [compiled_parity.json](compiled_parity.json): Saved compiled_parity.json record for prediction cost within native seed selection; the producer code defines its fields.

- [compiled_threshold_parity.json](compiled_threshold_parity.json): Saved compiled_threshold_parity.json record for prediction cost within native seed selection; the producer code defines its fields.

- [compiled_weights.bin](compiled_weights.bin): This file contains a saved model or its description.

- [parity.json](parity.json): Saved parity.json record for prediction cost within native seed selection; the producer code defines its fields.

- [threshold_policy.json](threshold_policy.json): Saved model parameters, policy settings, or a resumable training state.
