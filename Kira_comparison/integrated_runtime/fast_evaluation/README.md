# fast evaluation

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

[reduction_shared.patch](reduction_shared.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_check_pairs.cpp](s00_check_pairs.cpp)

The program compares all six modular features with the original ordered-pair calculation.

The required headers are `string`, `vector`, `algorithm`, `iostream`, `random`, `stdexcept`, `s15_shared_modular.h`.

The matching build script compiles this file into an executable.

Use the parent stage guide for the build order and input records.

[s01_check_seed.py](s01_check_seed.py)

The program checks bitwise probabilities and masks against the preceding compiled network.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s04_compiled_seed`, `s07_seed`, `s12_shared_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'seed_parity.json').write_text(json.dumps(data, indent=2) + '\n')
(EXP / 'families.json').read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/compiled_weights.bin').read_bytes()
(ROOT / '.tools/kira-shared-inference/libseed.so').read_bytes()

```

[s02_initial_freeze_generator.py](s02_initial_freeze_generator.py)

The program freezes implementation-only changes after exact and timing validation.

The module defines these callable interfaces:

```python

def sha(p)
def verify()
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = HERE / 'fast_evaluation'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(EXP / 'freeze.json').write_text(json.dumps(f, indent=2) + '\n')
(EXP / 'freeze.json').read_text()
(EXP / 'validation_summary.json').read_text()
(EXP / 'row_feature_check.json').read_text()
p.read_bytes()
(EXP / 'seed_parity.json').read_text()

```

## Data and supporting files

- [adoption.json](adoption.json): This file contains structured records from the parent calculation.

- [adoption_initial.json](adoption_initial.json): This file contains structured records from the parent calculation.

- [application_verification.json](application_verification.json): This file records checks of the corresponding calculation.

- [build.json](build.json): This file contains structured records from the parent calculation.

- [confirmation_summary.json](confirmation_summary.json): This file contains structured records from the parent calculation.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [freeze_initial.json](freeze_initial.json): This file contains structured records from the parent calculation.

- [release.json](release.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [row_feature_check.json](row_feature_check.json): This file records checks of the corresponding calculation.

- [seed_parity.json](seed_parity.json): This file records seed information or seed checks.

- [validation_summary.json](validation_summary.json): This file contains structured records from the parent calculation.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [shared_application_checks](shared_application_checks/README.md).

- [shared_confirmation](shared_confirmation/README.md).

- [shared_validation](shared_validation/README.md).
