# Equation filtering before expensive reduction work

This folder contains the code and records for equation filtering before expensive reduction work.

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
| [s00_contract.py](s00_contract.py) | Exact polynomial pre-reduction of the restricted vacuum identities. |
| [s01_application.py](s01_application.py) | Pre-reduces selected exact identities, then finish and check with Kira. |
| [s02_study.py](s02_study.py) | Fresh disjoint validation and reserved comparisons of exact pre-reduction. |
| [s03_run.sh](s03_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s04_check.py](s04_check.py) | Independent arithmetic, application, fallback and final-output checks. |
| [s05_run.sh](s05_run.sh) | Scheduler wrapper for run; its header sets the resource limits. |
| [s06_analyze.py](s06_analyze.py) | Matched complete-time ratios and exactness summaries. |
| [s07_plot.py](s07_plot.py) | Standalone plots from matched independent measurements. |
| [s08_document.py](s08_document.py) | Updates scientific text and READMEs from checked measurements. |
| [s09_release_check.py](s09_release_check.py) | Verify frozen code, exact evidence, report references and resource bounds. |
| [s10_report.sh](s10_report.sh) | Scheduler wrapper for report; its header sets the resource limits. |
| [s11_resume.sh](s11_resume.sh) | Scheduler wrapper for resume; its header sets the resource limits. |
| [s12_check_deployed.py](s12_check_deployed.py) | Verify the public deployed interface and its exact expanded output. |

## Data and supporting files

- [deployment.json](deployment.json): Saved deployment.json record for equation filtering before expensive reduction work; the producer code defines its fields.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [pilot_scheduler.log](pilot_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for equation filtering before expensive reduction work; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [resume_scheduler.log](resume_scheduler.log): This file contains saved program messages.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [development_pilot](development_pilot/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [pilot](pilot/README.md).

- [validation](validation/README.md).
