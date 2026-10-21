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
| [s15_generate_parallel.py](s15_generate_parallel.py) | Generate disjoint loop-order groups on four allocated CPU slots. |
| [s16_run_parallel_generation.sh](s16_run_parallel_generation.sh) | Scheduler wrapper for run parallel generation; its header sets the resource limits. |

## Data and supporting files

- [collection_audit.log](collection_audit.log): This file records checks of the corresponding calculation.

- [full_scheduler.log](full_scheduler.log): This file contains saved program messages.

- [generation_summary.json](generation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [integration_summary.json](integration_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_01_progress.json](loop_01_progress.json): Saved loop_01_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_01_summary.json](loop_01_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_02_progress.json](loop_02_progress.json): Saved loop_02_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_02_summary.json](loop_02_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_03_progress.json](loop_03_progress.json): Saved loop_03_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_03_summary.json](loop_03_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_04_progress.json](loop_04_progress.json): Saved loop_04_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_04_summary.json](loop_04_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_05_progress.json](loop_05_progress.json): Saved loop_05_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_05_summary.json](loop_05_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_06_progress.json](loop_06_progress.json): Saved loop_06_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_06_summary.json](loop_06_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_07_progress.json](loop_07_progress.json): Saved loop_07_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_07_summary.json](loop_07_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_08_progress.json](loop_08_progress.json): Saved loop_08_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_08_summary.json](loop_08_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_09_progress.json](loop_09_progress.json): Saved loop_09_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_09_summary.json](loop_09_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_10_progress.json](loop_10_progress.json): Saved loop_10_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_10_summary.json](loop_10_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_11_progress.json](loop_11_progress.json): Saved loop_11_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_11_summary.json](loop_11_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [loop_12_progress.json](loop_12_progress.json): Saved loop_12_progress.json record for the constructed integral collection; the producer code defines its fields.

- [loop_12_summary.json](loop_12_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [ml_roles_section_template.tex](ml_roles_section_template.tex): This file contains a LaTeX document or document section.

- [parallel_progress.json](parallel_progress.json): Saved parallel_progress.json record for the constructed integral collection; the producer code defines its fields.

- [parallel_scheduler.log](parallel_scheduler.log): This file contains saved program messages.

- [pilot_summary.json](pilot_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [pilot_validation.json](pilot_validation.json): Recorded checks of the calculation, data, or selected settings.

- [previous_catalog.json](previous_catalog.json): Execution messages and diagnostics for the named run.

- [previous_splits.json](previous_splits.json): Saved previous_splits.json record for the constructed integral collection; the producer code defines its fields.

- [previous_validation_summary.json](previous_validation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [progress.json](progress.json): Saved progress.json record for the constructed integral collection; the producer code defines its fields.

- [report_section_template.tex](report_section_template.tex): This file contains a LaTeX document or document section.

- [request.json](request.json): Physical inputs and target lists for the recorded experiment.

- [serial_generation_scheduler.log](serial_generation_scheduler.log): This file contains saved program messages.

- [validation.json](validation.json): This file records the completed validation checks.
