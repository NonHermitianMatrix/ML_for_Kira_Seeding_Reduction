# generalization

This folder tests new scattering structures and symbolic invariants.
It contains a massless nonplanar two-loop box, a massless pentagon and a box with external virtuality.
Seven batches contain 88 targets.
All seventy measured workflows pass exact checks.
All thirty-five filtered workflows require native fallback.
The complete-time ratio to native choices is 1.251829.
The application therefore defaults to native choices for these inputs.

`cases.json` defines the denominators, scalar products and targets.
`scattering_families/` contains rational parameter profiles.
`symbolic_kinematics/` contains independent symbolic invariants.
`optimal_paths/` contains finite minimum-operation checks for a bubble and a tadpole.
Each minimum applies to a stated source pool and operation cost.

Use `s12_reduce.py` for the application with a supplied basis.
Use `s02_study.py` for the recorded preparation and comparison stages.
The job wrappers supply the resource limits.
The application needs no reference target coefficients.
The mathematical checks and the timing tests use separate output files.

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
| [s00_native_run.py](s00_native_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s01_cases.py](s01_cases.py) | Defines new physical scattering families without using learned scores. |
| [s02_study.py](s02_study.py) | Frozen transfer tests with symbolic coefficients and exact native fallback. |
| [s03_job.sh](s03_job.sh) | Scheduler wrapper for job; its header sets the resource limits. |
| [s04_optimal_paths.py](s04_optimal_paths.py) | Certifies minimum counted field operations over every admissible finite pivot path. |
| [s05_verify_certificates.py](s05_verify_certificates.py) | Check every certificate edge independently using exact symbolic matrices. |
| [s06_pipeline.sh](s06_pipeline.sh) | Scheduler wrapper for pipeline; its header sets the resource limits. |
| [s07_audit.py](s07_audit.py) | Audit symbolic exports and test a larger seed region and fresh specializations. |
| [s08_analyze.py](s08_analyze.py) | Summarize complete times without selecting a new policy from the test. |
| [s09_audit_job.sh](s09_audit_job.sh) | Scheduler wrapper for audit job; its header sets the resource limits. |
| [s10_document.py](s10_document.py) | Write checked results and pin the report to the published data. |
| [s11_finish.sh](s11_finish.sh) | Scheduler wrapper for finish; its header sets the resource limits. |
| [s12_reduce.py](s12_reduce.py) | Reduces symbolic scattering targets using a supplied basis, without target answers. |
| [s13_application_check.py](s13_application_check.py) | Check the answer-free native application and its explicit experimental fallback. |
| [s14_application_job.sh](s14_application_job.sh) | Scheduler wrapper for application job; its header sets the resource limits. |

## Data and supporting files

- [cases.json](cases.json): This file defines the physical cases and requested targets.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for transfer to scattering structures and symbolic kinematics; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [runner_provenance.json](runner_provenance.json): Saved runner_provenance.json record for transfer to scattering structures and symbolic kinematics; the producer code defines its fields.

- [storage_audit.json](storage_audit.json): This file records checks of the corresponding calculation.

- [summary.json](summary.json): This file contains the result counts and summary measurements.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [application](application/README.md).

- [development](development/README.md).

- [logs](logs/README.md).

- [model_test](model_test/README.md).

- [optimal_paths](optimal_paths/README.md).

- [references](references/README.md).

- [scattering_families](scattering_families/README.md).

- [symbolic_kinematics](symbolic_kinematics/README.md).

## Later training study

This folder preserves the original fixed-model transfer test.
The [later scattering study](../../ML_model_equation_selection/scattering_training/README.md) adds training examples from these structures.
It tests new models on separate parameter points and symbolic target lists.
Its results do not replace the historical measurements above.

## Complete reduction cost

The [complete-cost study](../../ML_model_workflow_selection/README.md)
compares models that choose a full reduction strategy from measured time.
It combines seed bounds, saved seed and equation filters, integral ordering,
and the existing temporary database change.
It also compares separate target requests with their joint reduction.
The study includes full native IBP generation and all fallback costs.
It retains the earlier model weights and results.
Its native cases cover seven graph structures at one through three loops.
The restricted vacuum results through twelve loops remain a separate result.
See that folder for the frozen model, test summaries and application commands.
