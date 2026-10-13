# integration

This folder supports the calculation described in the parent guide.

Read [the parent guide](../README.md) for the stage and data flow.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Code files

The entries below follow file-name order.
Each entry gives its purpose and the input or output interface available in the source.

[interface.cpp.patch](interface.cpp.patch)

This patch records changes to the native Kira source.

The changed source paths are `interface.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[relations.cpp.patch](relations.cpp.patch)

This patch records changes to the native Kira source.

The changed source paths are `relations.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_equation_policy.h](s00_equation_policy.h)

The file provides learned equation filter. Exact IBP construction and algebra stay in Kira.

The required headers are `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `set`, `sstream`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s01_fast_equation_policy.h](s01_fast_equation_policy.h)

The file provides learned equation filter. Exact IBP construction and algebra stay in Kira.

The required headers are `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `set`, `sstream`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s02_cached_equation_policy.h](s02_cached_equation_policy.h)

The file provides learned equation filter. Exact IBP construction and algebra stay in Kira.

The required headers are `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `set`, `sstream`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s03_compact_equation_policy.h](s03_compact_equation_policy.h)

The file provides learned equation filter. Exact IBP construction and algebra stay in Kira.

The required headers are `array`, `chrono`, `cmath`, `cstring`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `set`, `sstream`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s04_lazy_equation_policy.h](s04_lazy_equation_policy.h)

The file provides learned equation filter. Exact IBP construction and algebra stay in Kira.

The required headers are `array`, `chrono`, `cmath`, `cstring`, `cstdlib`, `fstream`, `iomanip`, `map`, `mutex`, `set`, `sstream`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

## Data and supporting files

- [build.json](build.json): This file contains structured records from the parent calculation.

- [build_cached.json](build_cached.json): This file contains structured records from the parent calculation.

- [build_compact.json](build_compact.json): This file contains structured records from the parent calculation.

- [build_fast.json](build_fast.json): This file contains structured records from the parent calculation.

- [build_lazy.json](build_lazy.json): This file contains structured records from the parent calculation.

- [cached_verification.json](cached_verification.json): This file records checks of the corresponding calculation.

- [fast_verification.json](fast_verification.json): This file records checks of the corresponding calculation.

- [label_repeat.json.gz](label_repeat.json.gz): This file contains structured records from the parent calculation.

- [label_verification.json](label_verification.json): This file records checks of the corresponding calculation.

- [lazy_verification.json](lazy_verification.json): This file records checks of the corresponding calculation.

- [parity_cached_validation_00_sunrise_n21_kira-compact.json.gz](parity_cached_validation_00_sunrise_n21_kira-compact.json.gz): This file contains structured records from the parent calculation.

- [parity_cached_validation_00_sunrise_n21_kira-fast.json.gz](parity_cached_validation_00_sunrise_n21_kira-fast.json.gz): This file contains structured records from the parent calculation.

- [parity_cached_validation_01_double_box_n128_kira-compact.json.gz](parity_cached_validation_01_double_box_n128_kira-compact.json.gz): This file contains structured records from the parent calculation.

- [parity_cached_validation_01_double_box_n128_kira-fast.json.gz](parity_cached_validation_01_double_box_n128_kira-fast.json.gz): This file contains structured records from the parent calculation.

- [parity_cached_validation_02_vacuum3_n128_kira-compact.json.gz](parity_cached_validation_02_vacuum3_n128_kira-compact.json.gz): This file contains structured records from the parent calculation.

- [parity_cached_validation_02_vacuum3_n128_kira-fast.json.gz](parity_cached_validation_02_vacuum3_n128_kira-fast.json.gz): This file contains structured records from the parent calculation.

- [parity_lazy_validation_00_sunrise_n21_kira-compact.json.gz](parity_lazy_validation_00_sunrise_n21_kira-compact.json.gz): This file contains structured records from the parent calculation.

- [parity_lazy_validation_00_sunrise_n21_kira-lazy.json.gz](parity_lazy_validation_00_sunrise_n21_kira-lazy.json.gz): This file contains structured records from the parent calculation.

- [parity_lazy_validation_01_double_box_n128_kira-compact.json.gz](parity_lazy_validation_01_double_box_n128_kira-compact.json.gz): This file contains structured records from the parent calculation.

- [parity_lazy_validation_01_double_box_n128_kira-lazy.json.gz](parity_lazy_validation_01_double_box_n128_kira-lazy.json.gz): This file contains structured records from the parent calculation.

- [parity_lazy_validation_02_vacuum3_n128_kira-compact.json.gz](parity_lazy_validation_02_vacuum3_n128_kira-compact.json.gz): This file contains structured records from the parent calculation.

- [parity_lazy_validation_02_vacuum3_n128_kira-lazy.json.gz](parity_lazy_validation_02_vacuum3_n128_kira-lazy.json.gz): This file contains structured records from the parent calculation.

- [parity_validation_00_sunrise_n21_kira-fast.json.gz](parity_validation_00_sunrise_n21_kira-fast.json.gz): This file contains structured records from the parent calculation.

- [parity_validation_00_sunrise_n21_kira.json.gz](parity_validation_00_sunrise_n21_kira.json.gz): This file contains structured records from the parent calculation.

- [parity_validation_01_double_box_n128_kira-fast.json.gz](parity_validation_01_double_box_n128_kira-fast.json.gz): This file contains structured records from the parent calculation.

- [parity_validation_01_double_box_n128_kira.json.gz](parity_validation_01_double_box_n128_kira.json.gz): This file contains structured records from the parent calculation.

- [parity_validation_02_vacuum3_n128_kira-fast.json.gz](parity_validation_02_vacuum3_n128_kira-fast.json.gz): This file contains structured records from the parent calculation.

- [parity_validation_02_vacuum3_n128_kira.json.gz](parity_validation_02_vacuum3_n128_kira.json.gz): This file contains structured records from the parent calculation.

## Child folders

- [parity_before_feature_audit](parity_before_feature_audit/README.md).
