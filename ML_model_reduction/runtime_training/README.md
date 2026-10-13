# runtime training

This folder contains training inputs or saved training results.
Keep the stored family division unchanged.

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

[s00_runtime_policy.h](s00_runtime_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s01_modular_features.h](s01_modular_features.h)

The file provides bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.

The required headers are `array`, `algorithm`, `cmath`, `cctype`, `string`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s02_modular_policy.h](s02_modular_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s01_modular_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s03_test_features.cpp](s03_test_features.cpp)

The file provides standalone verification harness for modular coefficient features.

The required headers are `iostream`, `iomanip`, `string`, `vector`, `s01_modular_features.h`.

The matching build script compiles this file into an executable.

Use the parent stage guide for the build order and input records.

[s04_test_features.py](s04_test_features.py)

The program verifies modular values and row-cancellation estimates against exact SymPy arithmetic.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `sympy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'feature_tests.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 's01_modular_features.h').read_bytes()

```

[s05_train.py](s05_train.py)

The program fits compact row-cost trees with grouped validation and exact native cost labels.

The module defines these callable interfaces:

```python

def fit(x, y, weight, depth, minleaf)
def predict(nodes, x)
def evaluate(groups, nodes=None, gain=0, fill=False)
def main()

```

The imported external packages are `numpy`.

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPERIMENT = ROOT / 'Kira_comparison/integrated_runtime'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'training_results.json').write_text(json.dumps(report, indent=2) + '\n')
(EXPERIMENT / 'families.json').read_text()
(folder / 'model.json').write_text(json.dumps(model, indent=2) + '\n')
(folder / 'weights.txt').write_text('\n'.join(lines) + '\n')
path.read_bytes()

```

[s06_fast_features.h](s06_fast_features.h)

The file provides included inside namespace kira_cost, after Features and modular estimates exist.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s07_fast_policy.h](s07_fast_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s01_modular_features.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s08_policy_candidates.py](s08_policy_candidates.py)

The program initializes bounded policy families for optimization on full native trajectories.

The module defines these callable interfaces:

```python

def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trajectory_candidates.json').write_text(json.dumps(dict(candidates=out, objective='Choose coefficients from measured complete native trajectories on training families; use separate validation for deployment.'), indent=2) + '\n')
(p / 'weights.txt').write_text('\n'.join(['24 0 0', ' '.join(['0'] * 24), ' '.join(['1'] * 24), ' '.join(map(str, w))]) + '\n')

```

[s09_select_trajectory.py](s09_select_trajectory.py)

The program ranks learned row policies by complete training trajectories, keeping validation separate.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s03_records`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / 'Kira_comparison/integrated_runtime'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'trajectory_selection.json').write_text(json.dumps(selection, indent=2) + '\n')
(HERE / 'trajectory_candidates.json').read_text()
(EXP / 'families.json').read_text()
path.read_bytes()

```

[s10_sparse_policy.h](s10_sparse_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s01_modular_features.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s11_final_policy.h](s11_final_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s01_modular_features.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s12_cached_modular.h](s12_cached_modular.h)

The file provides bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.

The required headers are `array`, `cstdlib`, `algorithm`, `cmath`, `cctype`, `string`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s13_cached_policy.h](s13_cached_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s12_cached_modular.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s14_pair_policy.h](s14_pair_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s01_modular_features.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s15_shared_modular.h](s15_shared_modular.h)

The file provides bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.

The required headers are `array`, `algorithm`, `cmath`, `cctype`, `string`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s16_shared_policy.h](s16_shared_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s15_shared_modular.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s17_euclid_modular.h](s17_euclid_modular.h)

The file provides bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.

The required headers are `array`, `algorithm`, `cmath`, `cctype`, `string`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s18_euclid_policy.h](s18_euclid_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s17_euclid_modular.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s19_literal_modular.h](s19_literal_modular.h)

The file provides bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.

The required headers are `array`, `algorithm`, `cmath`, `cctype`, `string`, `unordered_map`, `vector`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s20_literal_policy.h](s20_literal_policy.h)

The file provides source-row cost policy for Kira; GPL-3.0-or-later.

The required headers are `algorithm`, `array`, `chrono`, `cmath`, `cstdlib`, `fstream`, `iomanip`, `numeric`, `stdexcept`, `string`, `vector`, `s19_literal_modular.h`, `s06_fast_features.h`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

## Data and supporting files

- [feature_tests.json](feature_tests.json): This file contains structured records from the parent calculation.

- [training_results.json](training_results.json): This file records training progress or training inputs.

- [trajectory_candidates.json](trajectory_candidates.json): This file records successive reduction states and checks.

- [trajectory_selection.json](trajectory_selection.json): This file records successive reduction states and checks.

## Child folders

- [candidates](candidates/README.md).

- [trajectory_candidates](trajectory_candidates/README.md).
