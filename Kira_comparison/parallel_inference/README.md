# parallel inference

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

[reduction_parallel.patch](reduction_parallel.patch)

This patch records changes to the native Kira source.

The changed source paths are `b/src/kira/reduction.cpp`.

Use the matching build script in the parent stage. Keep the required Kira source version.

[s00_check_arithmetic.cpp](s00_check_arithmetic.cpp)

The file provides exact checks for field inversion and all source-row features.

The required headers are `string`, `vector`, `algorithm`, `iostream`, `random`, `stdexcept`, `chrono`, `iomanip`, `s15_shared_modular.h`, `s19_literal_modular.h`.

The matching build script compiles this file into an executable.

Use the parent stage guide for the build order and input records.

[s01_check_seed.py](s01_check_seed.py)

The program checks bitwise probabilities and masks against the preceding compiled network.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`, `s07_seed`, `s12_shared_seed`, `s14_lane_seed`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent / 'integrated_runtime'
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'seed_parity.json').write_text(json.dumps(data, indent=2) + '\n')
(EXP / 'families.json').read_text()
(ROOT / 'ML_model_seed_selection/runtime_inference/compiled_weights.bin').read_bytes()
(ROOT / '.tools/kira-parallel-inference/libseed.so').read_bytes()

```

## Data and supporting files

- [adoption.json](adoption.json): This file contains structured records from the parent calculation.

- [application_verification.json](application_verification.json): This file records checks of the corresponding calculation.

- [arithmetic_check.json](arithmetic_check.json): This file records checks of the corresponding calculation.

- [build.json](build.json): This file contains structured records from the parent calculation.

- [confirmation_summary.json](confirmation_summary.json): This file contains structured records from the parent calculation.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [release.json](release.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [seed_parity.json](seed_parity.json): This file records seed information or seed checks.

- [validation_summary.json](validation_summary.json): This file contains structured records from the parent calculation.

- [verification.json](verification.json): This file records the independent checks.

## Child folders

- [application_checks](application_checks/README.md).

- [attempts](attempts/README.md).

- [confirmation](confirmation/README.md).

- [rejected_euclid](rejected_euclid/README.md).

- [shared](shared/README.md).

- [validation](validation/README.md).
