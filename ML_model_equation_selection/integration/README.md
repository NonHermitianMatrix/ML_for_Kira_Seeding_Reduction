# Native integration and build procedures

This folder contains the code and records for native integration and build procedures.

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
| [interface.cpp.patch](interface.cpp.patch) | This patch records changes to the native Kira source. |
| [relations.cpp.patch](relations.cpp.patch) | This patch records changes to the native Kira source. |
| [s00_equation_policy.h](s00_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |
| [s01_fast_equation_policy.h](s01_fast_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |
| [s02_cached_equation_policy.h](s02_cached_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |
| [s03_compact_equation_policy.h](s03_compact_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |
| [s04_lazy_equation_policy.h](s04_lazy_equation_policy.h) | Learned equation filter. Exact IBP construction and algebra stay in Kira. |

## Data and supporting files

- [build.json](build.json): Compiler, source, and executable information from the recorded build.

- [build_cached.json](build_cached.json): Saved build_cached.json record for native integration and build procedures; the producer code defines its fields.

- [build_compact.json](build_compact.json): Saved build_compact.json record for native integration and build procedures; the producer code defines its fields.

- [build_fast.json](build_fast.json): Saved build_fast.json record for native integration and build procedures; the producer code defines its fields.

- [build_lazy.json](build_lazy.json): Saved build_lazy.json record for native integration and build procedures; the producer code defines its fields.

- [cached_verification.json](cached_verification.json): This file records checks of the corresponding calculation.

- [fast_verification.json](fast_verification.json): This file records checks of the corresponding calculation.

- [label_repeat.json.gz](label_repeat.json.gz): Saved label_repeat.json.gz record for native integration and build procedures; the producer code defines its fields.

- [label_verification.json](label_verification.json): This file records checks of the corresponding calculation.

- [lazy_verification.json](lazy_verification.json): This file records checks of the corresponding calculation.

- [parity_cached_validation_00_sunrise_n21_kira-compact.json.gz](parity_cached_validation_00_sunrise_n21_kira-compact.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_cached_validation_00_sunrise_n21_kira-fast.json.gz](parity_cached_validation_00_sunrise_n21_kira-fast.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_cached_validation_01_double_box_n128_kira-compact.json.gz](parity_cached_validation_01_double_box_n128_kira-compact.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_cached_validation_01_double_box_n128_kira-fast.json.gz](parity_cached_validation_01_double_box_n128_kira-fast.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_cached_validation_02_vacuum3_n128_kira-compact.json.gz](parity_cached_validation_02_vacuum3_n128_kira-compact.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_cached_validation_02_vacuum3_n128_kira-fast.json.gz](parity_cached_validation_02_vacuum3_n128_kira-fast.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_lazy_validation_00_sunrise_n21_kira-compact.json.gz](parity_lazy_validation_00_sunrise_n21_kira-compact.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_lazy_validation_00_sunrise_n21_kira-lazy.json.gz](parity_lazy_validation_00_sunrise_n21_kira-lazy.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_lazy_validation_01_double_box_n128_kira-compact.json.gz](parity_lazy_validation_01_double_box_n128_kira-compact.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_lazy_validation_01_double_box_n128_kira-lazy.json.gz](parity_lazy_validation_01_double_box_n128_kira-lazy.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_lazy_validation_02_vacuum3_n128_kira-compact.json.gz](parity_lazy_validation_02_vacuum3_n128_kira-compact.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_lazy_validation_02_vacuum3_n128_kira-lazy.json.gz](parity_lazy_validation_02_vacuum3_n128_kira-lazy.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_validation_00_sunrise_n21_kira-fast.json.gz](parity_validation_00_sunrise_n21_kira-fast.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_validation_00_sunrise_n21_kira.json.gz](parity_validation_00_sunrise_n21_kira.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_validation_01_double_box_n128_kira-fast.json.gz](parity_validation_01_double_box_n128_kira-fast.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_validation_01_double_box_n128_kira.json.gz](parity_validation_01_double_box_n128_kira.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_validation_02_vacuum3_n128_kira-fast.json.gz](parity_validation_02_vacuum3_n128_kira-fast.json.gz): Recorded checks of the calculation, data, or selected settings.

- [parity_validation_02_vacuum3_n128_kira.json.gz](parity_validation_02_vacuum3_n128_kira.json.gz): Recorded checks of the calculation, data, or selected settings.

## Child folders

- [parity_before_feature_audit](parity_before_feature_audit/README.md).
