# early generation

This model selects seed--operator pairs before Kira constructs their coefficients.
It uses seventeen features that do not require symbolic equation coefficients.
The training set contains 153,124 candidate equations and 12,270 positive labels.
The labels record support in a native reference reduction.
They do not identify uniquely necessary equations.

Use `s12_reduce.py` to run this equation-selection experiment.
The selected tree has depth twelve for double-box requests.
It has depth eight for the tested vacuum and ladder requests.
Both trees use threshold 0.01.
The recorded 21-target sunrise request uses the preceding equation policy.
The native route retains native seed and row choices.

The comparison completed 280 workflows on eight new parameter profiles.
The complete-time ratio to native choices is 0.942907.
The preparation-time ratio is 0.637888.
All comparisons and eight additional applications pass exact checks.
These gains apply to the tested structures and rational kinematics with symbolic dimension.

Run the application from the project root in a scheduled job:

```bash
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s12_reduce.py --family-file FAMILY.json --masters-file MASTERS.json --size 128 --output ML_model_equation_selection/early_generation/application/RESULT.json.gz
```

The family file follows the case format in `families_test.json`.
The master file contains the prescribed master index list.
Choose a new output file.
The application does not need reference target coefficients.
An incomplete filtered attempt repeats with native equations and then with enlarged bounds.
A coefficient mismatch is an error.

The original development order includes build, collection, training, validation, composition tests, freeze, reserved tests and analysis.
The script entries below identify each stage.
Keep completed freeze records unchanged.
Use `s04_workflows.read` to read `early-shared-v1` records and their shared objects.
The reader checks the object hashes.

Each native attempt uses one thread and a 70-second limit.
References can use 90 seconds.
The address-space limit is 2,400 MiB.
The sampled process-tree memory limit is 2,100 MiB.
The scratch limit is 16 MiB.

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
| [s00_build.py](s00_build.py) | Compiles equation filtering and collection without changing prior binaries. |
| [s01_develop.sh](s01_develop.sh) | Scheduler wrapper for develop; its header sets the resource limits. |
| [s02_train.py](s02_train.py) | Fit a small target-dependent CART probability model using training groups only. |
| [s03_early_run.py](s03_early_run.py) | Run one bounded complete Kira reduction, retaining compact exact evidence. |
| [s04_workflows.py](s04_workflows.py) | Bounded native comparisons for decisions made before equation construction. |
| [s05_develop_fresh.sh](s05_develop_fresh.sh) | Scheduler wrapper for develop fresh; its header sets the resource limits. |
| [s06_validate.py](s06_validate.py) | Compare complete costs and choose validation candidates without reading reserved results. |
| [s07_validate.sh](s07_validate.sh) | Scheduler wrapper for validate; its header sets the resource limits. |
| [s08_parity.py](s08_parity.py) | Check the compiled early gate against saved Python probabilities on training candidates. |
| [s09_compact.py](s09_compact.py) | Stores repeated exact outputs once, verifying lossless record recovery. |
| [s10_composition.py](s10_composition.py) | Validates early equation filtering together with the existing trained row policy. |
| [s11_composition.sh](s11_composition.sh) | Scheduler wrapper for composition; its header sets the resource limits. |
| [s12_reduce.py](s12_reduce.py) | Run the frozen early equation policy with exact native fallback. |
| [s13_freeze.py](s13_freeze.py) | Freeze the validated policies, integration and reserved protocol before tests. |
| [s14_test.py](s14_test.py) | Evaluates the frozen policy on previously reserved physical profiles. |
| [s15_test.sh](s15_test.sh) | Scheduler wrapper for test; its header sets the resource limits. |
| [s16_seed_composition.py](s16_seed_composition.py) | Measures the existing seed model with early filtering before release selection. |
| [s17_seed_composition.sh](s17_seed_composition.sh) | Scheduler wrapper for seed composition; its header sets the resource limits. |
| [s18_analyze.py](s18_analyze.py) | Summarize fixed-test timings with physical-profile resampling. |
| [s19_plot.py](s19_plot.py) | Draws comparisons from the frozen, independently checked test results. |
| [s20_check_release.py](s20_check_release.py) | Verify deployment routing and preserve the preceding frozen releases. |
| [s21_document.py](s21_document.py) | Write the report and release summaries from audited fixed-test results. |
| [s22_finish.sh](s22_finish.sh) | Scheduler wrapper for finish; its header sets the resource limits. |

## Data and supporting files

- [additional_families.json](additional_families.json): Saved additional_families.json record for equation selection before coefficient construction; the producer code defines its fields.

- [families_test.json](families_test.json): Saved families_test.json record for equation selection before coefficient construction; the producer code defines its fields.

- [report_template.tex.in](report_template.tex.in): Saved report_template.tex.in record for equation selection before coefficient construction; the producer code defines its fields.

- [reserved_parameters.json](reserved_parameters.json): Saved reserved_parameters.json record for equation selection before coefficient construction; the producer code defines its fields.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [split_audit.json](split_audit.json): This file records checks of the corresponding calculation.

## Child folders

- [bottleneck_audit](bottleneck_audit/README.md).

- [development_overlap](development_overlap/README.md).

- [integration](integration/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [references](references/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
