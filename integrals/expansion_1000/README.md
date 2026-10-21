# The constructed integral collection

This folder contains the code and records for the constructed integral collection.

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
| [reduction_test_storage_before.py](reduction_test_storage_before.py) | Shared held-out metrics, bounded outputs and exact sample arithmetic. |
| [s00_exact.py](s00_exact.py) | Exact Laurent polynomials in d and m2, and an independent partial-fraction oracle. |
| [s01_generate.py](s01_generate.py) | Generate bounded coupled vacuum families and reverse constructions from their exact masters. |
| [s02_run_generation.sh](s02_run_generation.sh) | Scheduler wrapper for run generation; its header sets the resource limits. |
| [s03_validate.py](s03_validate.py) | Independent identity and reverse-record checks, including convergent radial integrals. |
| [s04_run_validation.sh](s04_run_validation.sh) | Scheduler wrapper for run validation; its header sets the resource limits. |
| [s05_integrate.py](s05_integrate.py) | Extends canonical catalogs and the existing grouped split after independent validation. |
| [s07_update_report.py](s07_update_report.py) | Finalizes the report after both expanded-data tests pass; keep immutable data citations. |
| [s08_finalize_training.py](s08_finalize_training.py) | Validates both expanded-data models and describe the current trained release. |
| [s09_run_training_validation.sh](s09_run_training_validation.sh) | Scheduler wrapper for run training validation; its header sets the resource limits. |
| [s10_validate_collection.py](s10_validate_collection.py) | Audit links and source hashes across the complete expanded collection. |
| [s11_run_collection_audit.sh](s11_run_collection_audit.sh) | Scheduler wrapper for run collection audit; its header sets the resource limits. |
| [s12_finalize_tests.py](s12_finalize_tests.py) | Records independently checked frozen tests and update affected READMEs. |
| [s13_build_report.sh](s13_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |
| [s14_stage_data.sh](s14_stage_data.sh) | Scheduler wrapper for stage data; its header sets the resource limits. |
| [s15_generate_parallel.py](s15_generate_parallel.py) | Generate disjoint loop-order groups on twelve allocated CPU slots. |
| [s16_run_parallel_generation.sh](s16_run_parallel_generation.sh) | Scheduler wrapper for run parallel generation; its header sets the resource limits. |
| [s17_validate_readers.py](s17_validate_readers.py) | Check gzip/XZ readers and new record links without model updates. |
| [s18_run_reader_validation.sh](s18_run_reader_validation.sh) | Scheduler wrapper for run reader validation; its header sets the resource limits. |
| [s19_compact_git.sh](s19_compact_git.sh) | Scheduler wrapper for compact git; its header sets the resource limits. |
| [s20_publish_release.py](s20_publish_release.py) | Publishes checked artifacts in the authorized data/model, test, report sequence. |
| [s21_run_publication.sh](s21_run_publication.sh) | Scheduler wrapper for run publication; its header sets the resource limits. |
| [s22_generate_group.py](s22_generate_group.py) | Generate disjoint loop groups in three bounded scheduler array tasks. |
| [s23_run_generation_groups.sh](s23_run_generation_groups.sh) | Scheduler wrapper for run generation groups; its header sets the resource limits. |
| [s24_combine_groups.py](s24_combine_groups.py) | Combines completed disjoint groups before independent mathematical validation. |
| [s25_run_group_validation.sh](s25_run_group_validation.sh) | Scheduler wrapper for run group validation; its header sets the resource limits. |
| [s26_run_test_publication.sh](s26_run_test_publication.sh) | Scheduler wrapper for run test publication; its header sets the resource limits. |
| [s27_run_report_update.sh](s27_run_report_update.sh) | Scheduler wrapper for run report update; its header sets the resource limits. |
| [s28_compress_records.py](s28_compress_records.py) | Compresss completed new families before the final independent checks. |
| [s29_run_compression.sh](s29_run_compression.sh) | Scheduler wrapper for run compression; its header sets the resource limits. |
| [s30_run_compression_pilot.sh](s30_run_compression_pilot.sh) | Scheduler wrapper for run compression pilot; its header sets the resource limits. |
| [s31_benchmark_cpu_threads.py](s31_benchmark_cpu_threads.py) | Measures CPU thread scaling on existing training examples without updating weights. |
| [s32_run_cpu_thread_pilot.sh](s32_run_cpu_thread_pilot.sh) | Scheduler wrapper for run cpu thread pilot; its header sets the resource limits. |
| [s33_benchmark_reduction_threads.py](s33_benchmark_reduction_threads.py) | Measures reduction-training CPU threads using saved training states only. |
| [s34_run_reduction_thread_pilot.sh](s34_run_reduction_thread_pilot.sh) | Scheduler wrapper for run reduction thread pilot; its header sets the resource limits. |
| [s35_run_validation_groups.sh](s35_run_validation_groups.sh) | Scheduler wrapper for run validation groups; its header sets the resource limits. |
| [s36_combine_validation.py](s36_combine_validation.py) | Combines disjoint, independently checked family groups without repeating calculations. |
| [s37_finalize_validation.sh](s37_finalize_validation.sh) | Scheduler wrapper for finalize validation; its header sets the resource limits. |
| [s38_check_parallel_preparation.py](s38_check_parallel_preparation.py) | Compare parallel preparation with saved training arrays, without model updates. |
| [s39_run_preparation_check.sh](s39_run_preparation_check.sh) | Scheduler wrapper for run preparation check; its header sets the resource limits. |
| [s40_validate_reduction_checkpoint.sh](s40_validate_reduction_checkpoint.sh) | Scheduler wrapper for validate reduction checkpoint; its header sets the resource limits. |
| [s41_check_git_blob_estimate.py](s41_check_git_blob_estimate.py) | Check the publication size estimate against bounded temporary Git objects. |
| [s42_compare_storage_scans.py](s42_compare_storage_scans.py) | Compare equivalent storage scans on immutable training features. |
| [s43_run_storage_scan_check.sh](s43_run_storage_scan_check.sh) | Scheduler wrapper for run storage scan check; its header sets the resource limits. |
| [s44_verify_storage_scan_resume.py](s44_verify_storage_scan_resume.py) | Proves that the resource-only scan update preserves predictive code and resume state. |
| [s45_resume_seed_training.sh](s45_resume_seed_training.sh) | Scheduler wrapper for resume seed training; its header sets the resource limits. |
| [s46_validate_report_release.py](s46_validate_report_release.py) | Check the rendered report against the frozen releases before publication. |
| [s47_run_report_publication.sh](s47_run_report_publication.sh) | Scheduler wrapper for run report publication; its header sets the resource limits. |
| [s48_refresh_git_cache.py](s48_refresh_git_cache.py) | Replaces a redundant full Git object cache with a verified partial clone. |
| [s49_run_git_cache_refresh.sh](s49_run_git_cache_refresh.sh) | Scheduler wrapper for run git cache refresh; its header sets the resource limits. |
| [s50_check_publication_storage_guard.py](s50_check_publication_storage_guard.py) | Check publication storage bounds against actual allocated fixture sizes. |
| [s51_check_partial_clone_staging.py](s51_check_partial_clone_staging.py) | Check bounded staging in a blob-filtered clone without fetching unchanged data. |
| [s52_complete_release.py](s52_complete_release.py) | Check the local report review and publish the final release records. |
| [s53_run_release_completion.sh](s53_run_release_completion.sh) | Scheduler wrapper for run release completion; its header sets the resource limits. |
| [seed_test_storage_before.py](seed_test_storage_before.py) | Evaluates the frozen trained model on every held-out target and save reproducible predictions. |

## Data and supporting files

This folder contains 111 data entries.
The names identify the family, case, target or repetition used by the parent reader.

- `.json`: 67 entries.

- `.log`: 19 entries.

- `.log.before_partial_commit_fix`: 2 entries.

- `.o15067261.1`: 1 entries.

- `.o15067261.2`: 1 entries.

- `.o15067261.3`: 1 entries.

- `.o15067268`: 1 entries.

- `.o15067508.1`: 1 entries.

- `.o15067508.2`: 1 entries.

- `.o15067508.3`: 1 entries.

- `.o15069248.1`: 1 entries.

- `.o15069248.2`: 1 entries.

- `.o15069248.3`: 1 entries.

- `.po15067261.1`: 1 entries.

- `.po15067261.2`: 1 entries.

- `.po15067261.3`: 1 entries.

- `.po15067268`: 1 entries.

- `.po15067508.1`: 1 entries.

- `.po15067508.2`: 1 entries.

- `.po15067508.3`: 1 entries.

- `.po15069248.1`: 1 entries.

- `.po15069248.2`: 1 entries.

- `.po15069248.3`: 1 entries.

- `.tex`: 2 entries.

- `.txt`: 1 entries.

Use the local manifest or the parent case list to match identifiers.
Keep compressed files in their stored format.
Read one record at a time with the parent reader.
