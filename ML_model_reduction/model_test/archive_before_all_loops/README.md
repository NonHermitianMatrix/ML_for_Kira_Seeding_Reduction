# archive before all loops

This folder retains an earlier stage, development check or saved comparison.
Use its records to interpret that stage.
Use the current parent application for a new calculation.

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

[s00_test_common.py](s00_test_common.py)

The file provides shared held-out metrics, bounded outputs and exact sample arithmetic.

The module defines these callable interfaces:

```python

def test_config()
def status(stage, **extra)
def signature()
def write_npz(path, **arrays)
def write_gzip(path, objects)
def csv_write(path, records)
def parsed(text)
def literal_int(node)
def coefficient(text, point, prime)
def eval_terms(terms, point, prime)
def exact_row_check(before, source, pivot, after, p)
def ordered_indices(probabilities, ids)
def classify(probabilities, reference, ids)
def reliability(confidence, correct, bins=10)
def metric_summary(data)
def merge_arrays(parts)
def ratio_summary(records, policy)

```

The imported external packages are `numpy`.

The imported project modules are `s00_common`, `s01_state`, `s05_predict`.

These source constants locate inputs and outputs:

```python

TEST = pathlib.Path(__file__).resolve().parent

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

np.savez_compressed(f, **arrays)

```

[s01_policies.py](s01_policies.py)

The file provides autonomous target-row policies and exact checks at independent stored samples.

The module defines these callable interfaces:

```python

def pools(identities, masters, prime, n)
def current_state(before, pivot, allowed, identities, family, masters, prime)
def greedy_choice(before, pivot, allowed, identities, masters, p)
def rollout(start, identities, pool, family, masters, prime, predictor, policy, cfg)
def sample_check(target, path, identities, master_columns, sample, cache)

```

The imported project modules are `s00_test_common`.

Import this helper module from the stage that uses it.

[s02_evaluate.py](s02_evaluate.py)

The file provides frozen held-out reference-state and autonomous reduction evaluation.

The module defines these callable interfaces:

```python

def family_evaluate(meta, predictor, cfg, sig)
def aggregate(summaries, cfg, sig, seconds)
def main()

```

The imported external packages are `torch`.

The imported project modules are `s00_test_common`, `s01_policies`.

The command accepts these parser options:

- `'--limit'`: type=int.

[s03_check_metrics.py](s03_check_metrics.py)

The file provides independent analytical checks before evaluating held-out families.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_test_common`.

This entry point uses the paths and options set in its source.

[s04_run_test.sh](s04_run_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTest
#$ -l h_rt=02:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/model_test/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
TEST_PYTHON=.tools/seed-model/venv/bin/python
"$TEST_PYTHON" ML_model_reduction/model_test/s03_check_metrics.py
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py --limit 2
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py

```

[s05_validate_outputs.py](s05_validate_outputs.py)

The file provides independent checks of saved predictions and complete finite-field trajectories.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_test_common`, `s01_policies`, `s05_predict`.

This entry point uses the paths and options set in its source.

[s06_plot_results.py](s06_plot_results.py)

The program generates six report figures from fixed saved held-out results.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_test_common`.

This entry point uses the paths and options set in its source.

[s07_update_report.py](s07_update_report.py)

The program writes the test section and documentation from validated fixed results.

The module defines these callable interfaces:

```python

def replace_text(path, old, new)
def marker(path, name, text)
def main()

```

The imported project modules are `s00_test_common`.

The command accepts these parser options:

- `'--validate-build'`: action='store_true'.

These calls show the stored input and output interface:

```python

path.read_text(encoding='utf-8')
path.write_text(body, encoding='utf-8')
(TEST / 'report_template.tex').read_text(encoding='utf-8')
(ROOT / 'report/reduction_test.tex').write_text(template, encoding='utf-8')
bib.read_text(encoding='utf-8')
path.write_text(text.replace(old, new), encoding='utf-8')
(ROOT / 'report/report.log').read_text(encoding='utf-8', errors='replace')
bib.write_text(content.rstrip() + '\n' + entries, encoding='utf-8')
report.read_text(encoding='utf-8')

```

[s08_finalize_report.sh](s08_finalize_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTestReport
#$ -l h_rt=02:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/model_test/finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
TEST_PYTHON=.tools/seed-model/venv/bin/python
"$TEST_PYTHON" ML_model_reduction/model_test/s09_validate_checkpoint.py
"$TEST_PYTHON" ML_model_reduction/model_test/s05_validate_outputs.py
"$TEST_PYTHON" ML_model_reduction/model_test/s06_plot_results.py
"$TEST_PYTHON" ML_model_reduction/model_test/s07_update_report.py
make -C report
"$TEST_PYTHON" ML_model_reduction/model_test/s07_update_report.py --validate-build

```

[s09_validate_checkpoint.py](s09_validate_checkpoint.py)

The program checks the current continued checkpoint without training or changing test outputs.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_test_common`, `s01_state`, `s05_predict`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(MODEL / 'trained_model.pt', map_location='cpu', weights_only=False)
torch.load(MODEL / 'runs/latest.pt', map_location='cpu', weights_only=False)

```

## Data and supporting files

- [additional_sample_failures.json](additional_sample_failures.json): This file contains structured records from the parent calculation.

- [checkpoint_validation.json](checkpoint_validation.json): This file records checks of the corresponding calculation.

- [confidence_reliability.csv](confidence_reliability.csv): This file supports the calculation described in the parent guide.

- [evaluation_request.json](evaluation_request.json): This file contains structured records from the parent calculation.

- [family_metrics.csv](family_metrics.csv): This file supports the calculation described in the parent guide.

- [family_metrics.json](family_metrics.json): This file contains structured records from the parent calculation.

- [figure_manifest.json](figure_manifest.json): This file lists related records and their identifiers.

- [figure_values.csv](figure_values.csv): This file supports the calculation described in the parent guide.

- [finalize.log](finalize.log): This file contains saved program messages.

- [launch.json](launch.json): This file contains structured records from the parent calculation.

- [metric_checks.json](metric_checks.json): This file records checks of the corresponding calculation.

- [paired_comparison.json](paired_comparison.json): This file contains structured records from the parent calculation.

- [pilot.json](pilot.json): This file contains structured records from the parent calculation.

- [report_template.tex](report_template.tex): This file contains a LaTeX document or document section.

- [report_validation.json](report_validation.json): This file contains structured records from the parent calculation.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [status.json](status.json): This file records the execution state.

- [target_metrics.jsonl.gz](target_metrics.jsonl.gz): This file records the target definitions or target identifiers.

- [test_config.json](test_config.json): This file contains structured records from the parent calculation.

- [test_results.json](test_results.json): This file contains structured records from the parent calculation.

- [tie_metrics.json](tie_metrics.json): This file contains structured records from the parent calculation.

- [validation.json](validation.json): This file records the completed validation checks.

- [validation_status.json](validation_status.json): This file records the execution state.

- [visual_review.json](visual_review.json): This file contains structured records from the parent calculation.

## Child folders

- [families](families/README.md).

- [figures](figures/README.md).
