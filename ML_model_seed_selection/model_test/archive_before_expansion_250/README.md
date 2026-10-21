# Archive before expansion 250: selection of IBP seeds

These records preserve development or earlier comparisons for selection of IBP seeds. They document the tested settings, including incomplete or rejected attempts.

This folder retains an earlier stage, development check or saved comparison.
Use its records to interpret that stage.
Use the current parent application for a new calculation.

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
| [s00_metrics.py](s00_metrics.py) | Reference-seed metrics at the fixed 0.5 threshold, with explicit empty-set handling. |
| [s01_evaluate.py](s01_evaluate.py) | Evaluates the frozen trained model on every held-out target and save reproducible predictions. |
| [s02_run_test.sh](s02_run_test.sh) | Scheduler wrapper for run test; its header sets the resource limits. |
| [s03_plot_results.py](s03_plot_results.py) | Create report figures from completed evaluation records without changing or rerunning the model. |
| [s04_validate_outputs.py](s04_validate_outputs.py) | Check saved prediction counts, confusion counts, hashes and graph files. |
| [s05_make_figures.sh](s05_make_figures.sh) | Scheduler wrapper for make figures; its header sets the resource limits. |
| [s06_update_report.py](s06_update_report.py) | Updates the scientific seed-model sections from the frozen expanded-data results. |
| [s07_build_report.sh](s07_build_report.sh) | Scheduler wrapper for build report; its header sets the resource limits. |

## Data and supporting files

- [confidence_reliability.csv](confidence_reliability.csv): Saved confidence_reliability.csv record for selection of IBP seeds; the producer code defines its fields.

- [curves.json](curves.json): Saved curves.json record for selection of IBP seeds; the producer code defines its fields.

- [family_metrics.csv](family_metrics.csv): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [family_metrics.json](family_metrics.json): Result counts and measured outcomes; interpret them with the stated comparison and limits.

- [figure_manifest.json](figure_manifest.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [metric_checks.json](metric_checks.json): This file records checks of the corresponding calculation.

- [per_target_metrics.jsonl.gz](per_target_metrics.jsonl.gz): This file records the target definitions or target identifiers.

- [prediction_manifest.json](prediction_manifest.json): Identifiers, file locations, or fixed settings used to reproduce this calculation.

- [probability_reliability.csv](probability_reliability.csv): Saved probability_reliability.csv record for selection of IBP seeds; the producer code defines its fields.

- [ranked_seed_recovery.csv](ranked_seed_recovery.csv): Saved ranked_seed_recovery.csv record for selection of IBP seeds; the producer code defines its fields.

- [report_section_template.tex](report_section_template.tex): This file contains a LaTeX document or document section.

- [report_values.json](report_values.json): Saved report_values.json record for selection of IBP seeds; the producer code defines its fields.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [test_results.json](test_results.json): Saved test_results.json record for selection of IBP seeds; the producer code defines its fields.

- [test_status.json](test_status.json): This file records the execution state.

- [training_history.csv](training_history.csv): This file records training progress or training inputs.

- [training_section_template.tex](training_section_template.tex): This file records training progress or training inputs.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [figures](figures/README.md).

- [predictions](predictions/README.md).
