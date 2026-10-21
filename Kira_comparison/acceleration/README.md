# Cost of learned reduction choices

These experiments test whether seed or row predictions save enough algebra to cover their own cost. They include compiled-policy tests, expression-level reduction, and separate component comparisons.

The inputs are stored target expressions or native reduction requests, depending on the named experiment. Outputs contain exact comparisons, elapsed times, and completion status. Development records select settings; validation and reserved results measure the fixed choices. Use the code table and the matching subfolder guide to select one experiment.

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
| [s00_prepare.py](s00_prepare.py) | Freeze development and evaluation families before new timing outcomes. |
| [s01_fast_seed.py](s01_fast_seed.py) | NumPy inference using the original seed model, public inputs and float32 weights. |
| [s02_export_seed.py](s02_export_seed.py) | Export frozen seed weights and verify inference using training families only. |
| [s03_seed_filter.h](s03_seed_filter.h) | Experimental individual-seed gate for Kira/pyRed; GPL-3.0-or-later. |
| [s04_build.py](s04_build.py) | Compiles the seed gate separately and link unchanged Kira objects. |
| [s05_setup.sh](s05_setup.sh) | Scheduler wrapper for setup; its header sets the resource limits. |
| [s06_worker.py](s06_worker.py) | One bounded native trial; labels are read only after reduction. |
| [s07_run.py](s07_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s08_run.sh](s08_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s09_fast_row.py](s09_fast_row.py) | NumPy inference with the unchanged reduction checkpoint. |
| [s10_export_row.py](s10_export_row.py) | Export the frozen row model and check numeric equivalence on bounded feature arrays. |
| [s11_row_server.py](s11_row_server.py) | Score admissible live Kira row operations with the frozen reduction model. |
| [s12_export_row.sh](s12_export_row.sh) | Scheduler wrapper for export row; its header sets the resource limits. |
| [s13_audit.py](s13_audit.py) | Independent modular checks of native exports and exact-update evidence. |
| [s14_summary.py](s14_summary.py) | Summarize all planned records, with separate failed and skipped observations. |
| [s15_array.sh](s15_array.sh) | Scheduler wrapper for array; its header sets the resource limits. |
| [s16_select_seeds.py](s16_select_seeds.py) | Select native IBP seeds from public family and target files. |
| [s17_update_report.py](s17_update_report.py) | Write checked native-acceleration results into the report. |
| [s20_freeze.py](s20_freeze.py) | Chooses the adapter on validation costs and freeze it before new cost tests. |
| [s21_freeze.sh](s21_freeze.sh) | Scheduler wrapper for freeze; its header sets the resource limits. |
| [s22_test_array.sh](s22_test_array.sh) | Scheduler wrapper for test array; its header sets the resource limits. |
| [s23_cpp_model.h](s23_cpp_model.h) | Native inference for the frozen source-row policy; GPL-3.0-or-later. |
| [s24_export_cpp.py](s24_export_cpp.py) | Write exact float32 row weights as C++ constants. |
| [s24_row_weights.h](s24_row_weights.h) | Frozen trained row weights; exported float32 values. |
| [s25_cpp_live_policy.h](s25_cpp_live_policy.h) | Live symbolic forward-elimination experiment; GPL-3.0-or-later. |
| [s26_build_cpp.py](s26_build_cpp.py) | Build native inference while preserving stock and earlier experimental binaries. |
| [s27_build_cpp.sh](s27_build_cpp.sh) | Scheduler wrapper for build cpp; its header sets the resource limits. |
| [s28_cpp_pilot.sh](s28_cpp_pilot.sh) | Scheduler wrapper for cpp pilot; its header sets the resource limits. |
| [s29_cpp_audit.py](s29_cpp_audit.py) | Check native coefficient sampling, features, probabilities and chosen updates. |
| [s30_cpp_pilot_v2.sh](s30_cpp_pilot_v2.sh) | Scheduler wrapper for cpp pilot v2; its header sets the resource limits. |
| [s31_plot.py](s31_plot.py) | Create exportable plots from completed, matched native comparisons. |
| [s32_finalize.sh](s32_finalize.sh) | Scheduler wrapper for finalize; its header sets the resource limits. |
| [s33_cpp_pilot_v3.sh](s33_cpp_pilot_v3.sh) | Scheduler wrapper for cpp pilot v3; its header sets the resource limits. |
| [s34_cpp_check.sh](s34_cpp_check.sh) | Scheduler wrapper for cpp check; its header sets the resource limits. |
| [s35_document.py](s35_document.py) | Updates documentation from the complete, independently checked comparison. |
| [s36_evidence.py](s36_evidence.py) | Content-addressed solver text: preserve evidence without repeated copies. |
| [s37_build_report.sh](s37_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |
| [s38_compact_records.py](s38_compact_records.py) | Deduplicates archived predictions/checks without changing any measured value. |
| [s39_records.py](s39_records.py) | Restores shared structured results and verify their unchanged logical content. |
| [s40_preflight_worker.py](s40_preflight_worker.py) | Native trials with Kira master-basis checking before symbolic elimination. |
| [s41_preflight_run.py](s41_preflight_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s42_preflight_pilot.sh](s42_preflight_pilot.sh) | Scheduler wrapper for preflight pilot; its header sets the resource limits. |
| [s43_adaptive_worker.py](s43_adaptive_worker.py) | Ranked seed expansion with an early native master-basis check. |
| [s44_adaptive_run.py](s44_adaptive_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s45_adaptive_pilot.sh](s45_adaptive_pilot.sh) | Scheduler wrapper for adaptive pilot; its header sets the resource limits. |
| [s46_adaptive_check.sh](s46_adaptive_check.sh) | Scheduler wrapper for adaptive check; its header sets the resource limits. |
| [s47_residual_worker.py](s47_residual_worker.py) | Residual-driven seed expansion with an early native master-basis check. |
| [s48_residual_run.py](s48_residual_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s49_residual_pilot.sh](s49_residual_pilot.sh) | Scheduler wrapper for residual pilot; its header sets the resource limits. |
| [s50_development_summary.py](s50_development_summary.py) | Summarize every early-admission development trial without claiming a timing test. |
| [s51_development_audit.sh](s51_development_audit.sh) | Scheduler wrapper for development audit; its header sets the resource limits. |
| [s52_development_report.py](s52_development_report.py) | Renders the checked, separate early-admission development results. |
| [s53_transfer_worker.py](s53_transfer_worker.py) | One bounded native trial; labels are read only after reduction. |
| [s54_transfer_run.py](s54_transfer_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s55_transfer_audit.py](s55_transfer_audit.py) | Independent modular checks of native exports and exact-update evidence. |
| [s56_transfer_test.sh](s56_transfer_test.sh) | Scheduler wrapper for transfer test; its header sets the resource limits. |
| [s57_transfer_summary.py](s57_transfer_summary.py) | Paired timing summary for the fixed two-loop transfer experiment. |
| [s58_transfer_plot.py](s58_transfer_plot.py) | Plot full-cost paired ratios for the fixed two-loop transfer check. |
| [s59_transfer_report.py](s59_transfer_report.py) | Renders the completed fixed-policy two-loop transfer comparison. |
| [s60_finish_transfer.sh](s60_finish_transfer.sh) | Scheduler wrapper for finish transfer; its header sets the resource limits. |
| [s61_evidence_archive.py](s61_evidence_archive.py) | Lossless high-dictionary compression of archived solver evidence. |
| [s62_compress_evidence.sh](s62_compress_evidence.sh) | Scheduler wrapper for compress evidence; its header sets the resource limits. |
| [s63_maintain_archive.sh](s63_maintain_archive.sh) | Scheduler wrapper for maintain archive; its header sets the resource limits. |
| [s64_resume_trials.py](s64_resume_trials.py) | Resumes storage-interrupted frozen trials on each original compute node. |
| [s65_expression_worker.py](s65_expression_worker.py) | Applies fast seed inference directly to complete stored target expressions. |
| [s66_expression_run.py](s66_expression_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s67_expression_pilot.sh](s67_expression_pilot.sh) | Scheduler wrapper for expression pilot; its header sets the resource limits. |
| [s68_expression_audit.py](s68_expression_audit.py) | Validates supplied-expression seed choices and raw Kira exports. |
| [s69_expression_preflight.py](s69_expression_preflight.py) | Check the master basis early for fast whole-expression seed selection. |
| [s70_expression_preflight_run.py](s70_expression_preflight_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s71_expression_preflight.sh](s71_expression_preflight.sh) | Scheduler wrapper for expression preflight; its header sets the resource limits. |
| [s72_expression_small.sh](s72_expression_small.sh) | Scheduler wrapper for expression small; its header sets the resource limits. |
| [s73_expression_policy_worker.py](s73_expression_policy_worker.py) | Dispatches whole-expression policies while preserving existing workers. |
| [s74_expression_policy_run.py](s74_expression_policy_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s75_expression_validation.sh](s75_expression_validation.sh) | Scheduler wrapper for expression validation; its header sets the resource limits. |
| [s76_expression_summary.py](s76_expression_summary.py) | Summarize whole-expression development and choose a validation interface. |
| [s77_expression_finish.sh](s77_expression_finish.sh) | Scheduler wrapper for expression finish; its header sets the resource limits. |
| [s78_expression_controls_worker.py](s78_expression_controls_worker.py) | Compare whole-expression learned seeds with exact Kira and a distance control. |
| [s79_expression_test_run.py](s79_expression_test_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s80_expression_test_audit.py](s80_expression_test_audit.py) | Validates supplied-expression seed choices and raw Kira exports. |
| [s81_expression_freeze.py](s81_expression_freeze.py) | Freeze the validation-selected whole-expression interface and submit confirmation. |
| [s82_expression_test_array.sh](s82_expression_test_array.sh) | Scheduler wrapper for expression test array; its header sets the resource limits. |
| [s83_expression_test_summary.py](s83_expression_test_summary.py) | Summarize frozen supplied-expression confirmation without discarding failures. |
| [s84_expression_finalize.sh](s84_expression_finalize.sh) | Scheduler wrapper for expression finalize; its header sets the resource limits. |
| [s85_expression_report.py](s85_expression_report.py) | Describes measured whole-expression reductions in the report. |
| [s86_finish_documentation.py](s86_finish_documentation.py) | Finishes release documentation after every declared comparison has been audited. |
| [s87_expression_plot.py](s87_expression_plot.py) | Plot complete-cost ratios for the frozen whole-expression confirmation. |
| [s88_matched_expression_worker.py](s88_matched_expression_worker.py) | Use the same early master admission for learned and distance-selected seeds. |
| [s89_matched_expression_run.py](s89_matched_expression_run.py) | Counterbalanced complete trials, with bounded time, memory and scratch. |
| [s90_matched_expression_array.sh](s90_matched_expression_array.sh) | Scheduler wrapper for matched expression array; its header sets the resource limits. |
| [s91_matched_expression_audit.py](s91_matched_expression_audit.py) | Validates supplied-expression seed choices and raw Kira exports. |
| [s92_matched_expression_summary.py](s92_matched_expression_summary.py) | Summarize frozen supplied-expression confirmation without discarding failures. |
| [s93_matched_expression_finalize.sh](s93_matched_expression_finalize.sh) | Scheduler wrapper for matched expression finalize; its header sets the resource limits. |
| [s94_matched_expression_report.py](s94_matched_expression_report.py) | Reports the confirmation with identical admission checks for both selectors. |
| [s95_release_checks.py](s95_release_checks.py) | Check all declared comparison outputs before publishing the release. |
| [s96_prepare_release.sh](s96_prepare_release.sh) | Scheduler wrapper for prepare release; its header sets the resource limits. |

## Data and supporting files

This folder contains 193 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.csv`: 1 entries.

- `.json`: 60 entries.

- `.lock`: 2 entries.

- `.log`: 17 entries.

- `.npz`: 2 entries.

- `.o15109644`: 1 entries.

- `.o15109645`: 1 entries.

- `.o15109663`: 1 entries.

- `.o15109664`: 1 entries.

- `.o15109667`: 1 entries.

- `.o15109668`: 1 entries.

- `.o15109674`: 1 entries.

- `.o15109695`: 1 entries.

- `.o15109697`: 1 entries.

- `.o15109702.1`: 1 entries.

- `.o15109702.2`: 1 entries.

- `.o15109702.3`: 1 entries.

- `.o15109702.4`: 1 entries.

- `.o15109702.5`: 1 entries.

- `.o15109702.6`: 1 entries.

- `.o15109980.1`: 1 entries.

- `.o15109980.10`: 1 entries.

- `.o15109980.11`: 1 entries.

- `.o15109980.12`: 1 entries.

- `.o15109980.13`: 1 entries.

- `.o15109980.14`: 1 entries.

- `.o15109980.15`: 1 entries.

- `.o15109980.16`: 1 entries.

- `.o15109980.17`: 1 entries.

- `.o15109980.18`: 1 entries.

- `.o15109980.19`: 1 entries.

- `.o15109980.2`: 1 entries.

- `.o15109980.20`: 1 entries.

- `.o15109980.21`: 1 entries.

- `.o15109980.22`: 1 entries.

- `.o15109980.23`: 1 entries.

- `.o15109980.24`: 1 entries.

- `.o15109980.3`: 1 entries.

- `.o15109980.4`: 1 entries.

- `.o15109980.5`: 1 entries.

- `.o15109980.6`: 1 entries.

- `.o15109980.7`: 1 entries.

- `.o15109980.8`: 1 entries.

- `.o15109980.9`: 1 entries.

- `.o15110075`: 1 entries.

- `.o15110079`: 1 entries.

- `.o15110100`: 1 entries.

- `.o15110144`: 1 entries.

- `.o15110161`: 1 entries.

- `.o15110183`: 1 entries.

- `.o15110184`: 1 entries.

- `.o15110185`: 1 entries.

- `.o15110186`: 1 entries.

- `.o15110187`: 1 entries.

- `.o15110188`: 1 entries.

- `.o15110189`: 1 entries.

- `.o15110221`: 1 entries.

- `.o15110236`: 1 entries.

- `.o15110286`: 1 entries.

- `.o15110287`: 1 entries.

- `.o15110329`: 1 entries.

- `.o15110345.1`: 1 entries.

- `.o15110345.2`: 1 entries.

- `.o15110345.3`: 1 entries.

- `.o15110345.4`: 1 entries.

- `.o15110345.5`: 1 entries.

- `.o15110345.6`: 1 entries.

- `.o15110549.1`: 1 entries.

- `.o15110549.10`: 1 entries.

- `.o15110549.11`: 1 entries.

- `.o15110549.12`: 1 entries.

- `.o15110549.13`: 1 entries.

- `.o15110549.14`: 1 entries.

- `.o15110549.15`: 1 entries.

- `.o15110549.16`: 1 entries.

- `.o15110549.17`: 1 entries.

- `.o15110549.18`: 1 entries.

- `.o15110549.19`: 1 entries.

- `.o15110549.2`: 1 entries.

- `.o15110549.20`: 1 entries.

- `.o15110549.21`: 1 entries.

- `.o15110549.22`: 1 entries.

- `.o15110549.23`: 1 entries.

- `.o15110549.24`: 1 entries.

- `.o15110549.3`: 1 entries.

- `.o15110549.4`: 1 entries.

- `.o15110549.5`: 1 entries.

- `.o15110549.6`: 1 entries.

- `.o15110549.7`: 1 entries.

- `.o15110549.8`: 1 entries.

- `.o15110549.9`: 1 entries.

- `.o15110588.1`: 1 entries.

- `.o15110588.10`: 1 entries.

- `.o15110588.11`: 1 entries.

- `.o15110588.12`: 1 entries.

- `.o15110588.13`: 1 entries.

- `.o15110588.14`: 1 entries.

- `.o15110588.15`: 1 entries.

- `.o15110588.16`: 1 entries.

- `.o15110588.17`: 1 entries.

- `.o15110588.18`: 1 entries.

- `.o15110588.19`: 1 entries.

- `.o15110588.2`: 1 entries.

- `.o15110588.20`: 1 entries.

- `.o15110588.21`: 1 entries.

- `.o15110588.22`: 1 entries.

- `.o15110588.23`: 1 entries.

- `.o15110588.24`: 1 entries.

- `.o15110588.3`: 1 entries.

- `.o15110588.4`: 1 entries.

- `.o15110588.5`: 1 entries.

- `.o15110588.6`: 1 entries.

- `.o15110588.7`: 1 entries.

- `.o15110588.8`: 1 entries.

- `.o15110588.9`: 1 entries.

- `no suffix`: 1 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.

## Child folders

- [adaptive_pilot](adaptive_pilot/README.md).

- [adaptive_validation](adaptive_validation/README.md).

- [combined_pilot](combined_pilot/README.md).

- [component_pilot](component_pilot/README.md).

- [cpp_initial](cpp_initial/README.md).

- [cpp_pilot](cpp_pilot/README.md).

- [cpp_pilot_v2](cpp_pilot_v2/README.md).

- [cpp_pilot_v3](cpp_pilot_v3/README.md).

- [cpp_v2](cpp_v2/README.md).

- [development_extra](development_extra/README.md).

- [evidence](evidence/README.md).

- [expression_matched](expression_matched/README.md).

- [expression_pilot](expression_pilot/README.md).

- [expression_preflight](expression_preflight/README.md).

- [expression_small](expression_small/README.md).

- [expression_test](expression_test/README.md).

- [expression_thresholds](expression_thresholds/README.md).

- [expression_v1](expression_v1/README.md).

- [expression_validation](expression_validation/README.md).

- [pilot](pilot/README.md).

- [preflight_pilot](preflight_pilot/README.md).

- [residual_pilot](residual_pilot/README.md).

- [results](results/README.md).

- [row_source_pilot](row_source_pilot/README.md).

- [structured_evidence](structured_evidence/README.md).

- [transfer_test](transfer_test/README.md).

- [validation](validation/README.md).
