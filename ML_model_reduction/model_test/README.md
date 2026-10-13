# model test

This folder contains reserved test inputs, outputs or checks.
Keep these records outside model fitting and threshold selection.

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

def storage_guard(full=False)
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
- `'--worker'`: type=int.
- `'--workers'`: type=int; default=1.
- `'--aggregate-only'`: action='store_true'.

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

The source comments describe complete aggregation, output checks and plots with s12_finalize_test.sh.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTest
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -pe shared 4
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
python3 - <<'GATE'
import json
from pathlib import Path
p=Path("integrals/expansion_1000/publication.json")
r=json.loads(p.read_text());assert r["training"]["status"]=="pushed"
assert json.loads(Path("integrals/expansion_1000/training_release.json").read_text())["status"]=="both_models_validated"
GATE
TEST_PYTHON=.tools/seed-model/venv/bin/python
if [[ "${1:-}" == "--plots-only" ]]; then
  "$TEST_PYTHON" ML_model_reduction/model_test/s06_plot_results.py
  exit 0
fi
"$TEST_PYTHON" ML_model_reduction/model_test/s03_check_metrics.py
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py --limit 2
"$TEST_PYTHON" ML_model_reduction/model_test/s10_parallel_test.py --workers-only

# Complete aggregation, output checks and plots with s12_finalize_test.sh.

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

The program updates the reduction training and held-out sections from independently checked records.

The module defines these callable interfaces:

```python

def render(name, values)
def main()

```

The imported project modules are `s00_test_common`.

These source constants locate inputs and outputs:

```python

REPORT = ROOT / 'report'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(TEST / name).read_text(encoding='utf-8')
(REPORT / 'reduction_training.tex').write_text(render('training_section_template.tex', v), encoding='utf-8')
(REPORT / 'reduction_test.tex').write_text(render('report_template.tex', v), encoding='utf-8')

```

[s08_finalize_report.sh](s08_finalize_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The source comments describe current combined report: requires --data-commit and --test-commit.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandedReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o ML_model_reduction/model_test/finalize.log
set -euo pipefail
# Current combined report: requires --data-commit and --test-commit.
exec bash integrals/higher_loops/s13_build_report.sh "$@"

```

[s09_validate_checkpoint.py](s09_validate_checkpoint.py)

The program validates twenty expanded-data passes and freeze the exact checkpoint for testing.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `torch`.

The imported project modules are `s00_test_common`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(MODEL / 'trained_model.pt', map_location='cpu', weights_only=False)
torch.load(MODEL / 'runs/all_loops_latest.pt', map_location='cpu', weights_only=False)

```

[s10_parallel_test.py](s10_parallel_test.py)

The program evaluates disjoint held-out families on four allocated CPU slots, then aggregate.

The module defines these callable interfaces:

```python

def read(p)
def write(p, obj)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

```

The command accepts these parser options:

- `'--workers-only'`: action='store_true'.

These calls show the stored input and output interface:

```python

tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')

```

[s11_validate_trained.sh](s11_validate_trained.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionWeights
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o ML_model_reduction/model_test/checkpoint_validation.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/model_test/s09_validate_checkpoint.py

```

[s12_finalize_test.sh](s12_finalize_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionSummary
#$ -l h_rt=06:00:00,h_data=10G
#$ -j y
#$ -o ML_model_reduction/model_test/finalize_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.tools/reduction-model/matplotlib"
mkdir -p "$MPLCONFIGDIR"
ulimit -v 8388608
ulimit -f 131072
ulimit -c 0
TEST_PYTHON=.tools/seed-model/venv/bin/python
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py --aggregate-only
"$TEST_PYTHON" ML_model_reduction/model_test/s05_validate_outputs.py
"$TEST_PYTHON" ML_model_reduction/model_test/s06_plot_results.py
"$TEST_PYTHON" - <<'PY'
import json
from pathlib import Path
p=Path("ML_model_reduction/model_test/parallel_execution.json")
r=json.loads(p.read_text());assert r["status"]=="workers_complete"
r["status"]="complete";r["aggregation_separate_memory_allocation"]=True
p.write_text(json.dumps(r,indent=2)+"\n")
PY

```

## Data and supporting files

- [checkpoint_validation.json](checkpoint_validation.json): This file records checks of the corresponding calculation.

- [confidence_reliability.csv](confidence_reliability.csv): This file supports the calculation described in the parent guide.

- [family_metrics.csv](family_metrics.csv): This file supports the calculation described in the parent guide.

- [family_metrics.json](family_metrics.json): This file contains structured records from the parent calculation.

- [figure_manifest.json](figure_manifest.json): This file lists related records and their identifiers.

- [figure_values.csv](figure_values.csv): This file supports the calculation described in the parent guide.

- [finalize_scheduler.log](finalize_scheduler.log): This file contains saved program messages.

- [finalize_scheduler_before_storage_guard.log](finalize_scheduler_before_storage_guard.log): This file contains saved program messages.

- [metric_checks.json](metric_checks.json): This file records checks of the corresponding calculation.

- [paired_comparison.json](paired_comparison.json): This file contains structured records from the parent calculation.

- [parallel_execution.json](parallel_execution.json): This file contains structured records from the parent calculation.

- [pilot.json](pilot.json): This file contains structured records from the parent calculation.

- [report_template.tex](report_template.tex): This file contains a LaTeX document or document section.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [scheduler_before_storage_guard.log](scheduler_before_storage_guard.log): This file contains saved program messages.

- [status.json](status.json): This file records the execution state.

- [target_metrics.jsonl.gz](target_metrics.jsonl.gz): This file records the target definitions or target identifiers.

- [test_config.json](test_config.json): This file contains structured records from the parent calculation.

- [test_results.json](test_results.json): This file contains structured records from the parent calculation.

- [tie_metrics.json](tie_metrics.json): This file contains structured records from the parent calculation.

- [training_section_template.tex](training_section_template.tex): This file records training progress or training inputs.

- [validation.json](validation.json): This file records the completed validation checks.

- [validation_status.json](validation_status.json): This file records the execution state.

- [worker_00.log](worker_00.log): This file contains saved program messages.

- [worker_00_status.json](worker_00_status.json): This file records the execution state.

- [worker_01.log](worker_01.log): This file contains saved program messages.

- [worker_01_status.json](worker_01_status.json): This file records the execution state.

- [worker_02.log](worker_02.log): This file contains saved program messages.

- [worker_02_status.json](worker_02_status.json): This file records the execution state.

- [worker_03.log](worker_03.log): This file contains saved program messages.

- [worker_03_status.json](worker_03_status.json): This file records the execution state.

## Child folders

- [archive_before_all_loops](archive_before_all_loops/README.md).

- [archive_before_expansion_250](archive_before_expansion_250/README.md).

- [families](families/README.md).

- [figures](figures/README.md).
