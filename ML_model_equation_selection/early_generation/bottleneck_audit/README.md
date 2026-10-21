# Bottleneck audit: equation selection before coefficient construction

This folder contains the code and records for equation selection before coefficient construction.

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
| [s00_timestamp.py](s00_timestamp.py) | This module supports the local calculation. |
| [s01_profile.py](s01_profile.py) | This module supports the local calculation. |
| [s02_profile.sh](s02_profile.sh) | Scheduler wrapper for profile; its header sets the resource limits. |
| [s03_profile_run.py](s03_profile_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s04_summarize.py](s04_summarize.py) | Summarize non-overlapping diagnostic log intervals and existing native timers. |

## Data and supporting files

- [completed.json](completed.json): Saved completed.json record for equation selection before coefficient construction; the producer code defines its fields.

- [equation_test_00_sunrise_n21_r0.json.gz](equation_test_00_sunrise_n21_r0.json.gz): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r0_events.json](equation_test_00_sunrise_n21_r0_events.json): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r1.json.gz](equation_test_00_sunrise_n21_r1.json.gz): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r1_events.json](equation_test_00_sunrise_n21_r1_events.json): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r2.json.gz](equation_test_00_sunrise_n21_r2.json.gz): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r2_events.json](equation_test_00_sunrise_n21_r2_events.json): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r0.json.gz](equation_test_02_double_box_n128_r0.json.gz): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r0_events.json](equation_test_02_double_box_n128_r0_events.json): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r1.json.gz](equation_test_02_double_box_n128_r1.json.gz): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r1_events.json](equation_test_02_double_box_n128_r1_events.json): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r2.json.gz](equation_test_02_double_box_n128_r2.json.gz): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r2_events.json](equation_test_02_double_box_n128_r2_events.json): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r0.json.gz](equation_test_06_ladder3_n128_r0.json.gz): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r0_events.json](equation_test_06_ladder3_n128_r0_events.json): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r1.json.gz](equation_test_06_ladder3_n128_r1.json.gz): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r1_events.json](equation_test_06_ladder3_n128_r1_events.json): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r2.json.gz](equation_test_06_ladder3_n128_r2.json.gz): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r2_events.json](equation_test_06_ladder3_n128_r2_events.json): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r0.json.gz](equation_test_07_ladder3_n128_r0.json.gz): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r0_events.json](equation_test_07_ladder3_n128_r0_events.json): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r1.json.gz](equation_test_07_ladder3_n128_r1.json.gz): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r1_events.json](equation_test_07_ladder3_n128_r1_events.json): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r2.json.gz](equation_test_07_ladder3_n128_r2.json.gz): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r2_events.json](equation_test_07_ladder3_n128_r2_events.json): This file records the source equations or their checks.

- [initial_wrapper_guard_failure.json.gz](initial_wrapper_guard_failure.json.gz): Saved initial_wrapper_guard_failure.json.gz record for equation selection before coefficient construction; the producer code defines its fields.

- [initial_wrapper_guard_failure.log](initial_wrapper_guard_failure.log): This file contains saved program messages.

- [job.log](job.log): This file contains saved program messages.

- [summary.json](summary.json): This file contains the result counts and summary measurements.
