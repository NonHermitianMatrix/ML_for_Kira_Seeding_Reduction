# Restricted vacuum reductions across loop orders

This folder contains the code and records for restricted vacuum reductions across loop orders.

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
| [s06_run_all_loops.sh](s06_run_all_loops.sh) | Scheduler wrapper for run all loops; its header sets the resource limits. |
| [s07_update_report.py](s07_update_report.py) | Finalizes the report after both expanded-data tests pass; keep immutable data citations. |
| [s08_finalize_training.py](s08_finalize_training.py) | Validates both expanded-data models and describe the current trained release. |
| [s09_run_training_validation.sh](s09_run_training_validation.sh) | Scheduler wrapper for run training validation; its header sets the resource limits. |
| [s10_validate_collection.py](s10_validate_collection.py) | Audit links and source hashes across the complete expanded collection. |
| [s11_run_collection_audit.sh](s11_run_collection_audit.sh) | Scheduler wrapper for run collection audit; its header sets the resource limits. |
| [s12_finalize_tests.py](s12_finalize_tests.py) | Records independently checked frozen tests and update affected READMEs. |
| [s13_build_report.sh](s13_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |
| [s14_stage_data.sh](s14_stage_data.sh) | Scheduler wrapper for stage data; its header sets the resource limits. |

## Data and supporting files

- [collection_audit.log](collection_audit.log): This file records checks of the corresponding calculation.

- [full_scheduler.log](full_scheduler.log): This file contains saved program messages.

- [generation_summary.json](generation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [integration_summary.json](integration_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [ml_roles_section_template.tex](ml_roles_section_template.tex): This file contains a LaTeX document or document section.

- [original_validation_summary.json](original_validation_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [pilot_summary.json](pilot_summary.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [pilot_validation.json](pilot_validation.json): Recorded checks of the calculation, data, or selected settings.

- [progress.json](progress.json): Saved progress.json record for restricted vacuum reductions across loop orders; the producer code defines its fields.

- [report_build.log](report_build.log): This file contains saved program messages.

- [report_build_final.log](report_build_final.log): This file contains saved program messages.

- [report_section_template.tex](report_section_template.tex): This file contains a LaTeX document or document section.

- [report_update.json](report_update.json): Saved report_update.json record for restricted vacuum reductions across loop orders; the producer code defines its fields.

- [request.json](request.json): Physical inputs and target lists for the recorded experiment.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [test_release.json](test_release.json): Saved test_release.json record for restricted vacuum reductions across loop orders; the producer code defines its fields.

- [training_release.json](training_release.json): This file records training progress or training inputs.

- [training_validation_resume_scheduler.log](training_validation_resume_scheduler.log): This file records training progress or training inputs.

- [training_validation_scheduler.log](training_validation_scheduler.log): This file records training progress or training inputs.

- [validation.json](validation.json): This file records the completed validation checks.

- [validation_scheduler.log](validation_scheduler.log): This file contains saved program messages.
