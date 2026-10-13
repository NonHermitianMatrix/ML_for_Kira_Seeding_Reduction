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

[s00_metrics.py](s00_metrics.py)

The file provides reference-seed metrics at the fixed 0.5 threshold, with explicit empty-set handling.

The module defines these callable interfaces:

```python

def divide(a, b)
def micro_metrics(tn, fp, fn, tp)
def target_metrics(p, y, seeds)
class Aggregate
class Curves
def self_check()

```

The imported external packages are `numpy`.

Import this helper module from the stage that uses it.

[s01_evaluate.py](s01_evaluate.py)

The program evaluates the frozen trained model on every held-out target and save reproducible predictions.

The module defines these callable interfaces:

```python

def sha(path)
def write_json(path, data)
def storage_guard()
def main()

```

The imported external packages are `numpy`, `torch`.

The imported project modules are `s00_metrics`, `s01_data`, `s02_model`, `s04_predict`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
MODEL = HERE.parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

temp.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')

```

[s02_run_test.sh](s02_run_test.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedTest
#$ -l h_rt=06:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/model_test/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.tools/seed-model/matplotlib"
mkdir -p "$MPLCONFIGDIR"
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
timeout 21300s .tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s01_evaluate.py

.tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s03_plot_results.py
.tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s04_validate_outputs.py

```

[s03_plot_results.py](s03_plot_results.py)

The program creates report figures from completed evaluation records without changing or rerunning the model.

The module defines these callable interfaces:

```python

def read(p)
def csv_write(name, rows)
def main()

```

The imported external packages are `matplotlib`, `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
MODEL = HERE.parent
REPORT = MODEL.parent / 'report'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'figure_manifest.json').write_text(json.dumps(dict(figures=saved, formats=['pdf', 'png'], report_copies='report/figures', matplotlib_version=matplotlib.__version__), indent=2) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')

```

[s04_validate_outputs.py](s04_validate_outputs.py)

The program checks saved prediction counts, confusion counts, hashes and graph files.

The module defines these callable interfaces:

```python

def read(p)
def sha(p)
def main()

```

The imported external packages are `numpy`.

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')

```

[s05_make_figures.sh](s05_make_figures.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraTestFigures
#$ -l h_rt=00:30:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/model_test/figures.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.tools/seed-model/matplotlib"
mkdir -p "$MPLCONFIGDIR"
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
timeout 600s .tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s03_plot_results.py
timeout 600s .tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s04_validate_outputs.py

```

[s06_update_report.py](s06_update_report.py)

The program updates the scientific seed-model sections from the frozen expanded-data results.

The module defines these callable interfaces:

```python

def read(p)
def render(name, values)
def main()

```

These source constants locate inputs and outputs:

```python

HERE = pathlib.Path(__file__).resolve().parent
MODEL = HERE.parent
REPORT = ROOT / 'report'

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / name).read_text(encoding='utf-8')
path.read_text(encoding='utf-8')
path.write_text(s, encoding='utf-8')
(REPORT / 'seed_model_test.tex').write_text(render('report_section_template.tex', values), encoding='utf-8')
(HERE / 'report_values.json').write_text(json.dumps(values, indent=2) + '\n', encoding='utf-8')
p.read_text(encoding='utf-8')

```

[s07_build_report.sh](s07_build_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraTestReport
#$ -l h_rt=00:10:00,h_data=2G
#$ -j y
#$ -o ML_model_seed_selection/model_test/report_build.log
set -euo pipefail
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
make -C report

```

## Data and supporting files

- [confidence_reliability.csv](confidence_reliability.csv): This file supports the calculation described in the parent guide.

- [curves.json](curves.json): This file contains structured records from the parent calculation.

- [family_metrics.csv](family_metrics.csv): This file supports the calculation described in the parent guide.

- [family_metrics.json](family_metrics.json): This file contains structured records from the parent calculation.

- [figure_manifest.json](figure_manifest.json): This file lists related records and their identifiers.

- [interruption_before_storage_guard.json](interruption_before_storage_guard.json): This file contains structured records from the parent calculation.

- [metric_checks.json](metric_checks.json): This file records checks of the corresponding calculation.

- [original_inference_allocation.json](original_inference_allocation.json): This file contains structured records from the parent calculation.

- [per_target_metrics.jsonl.gz](per_target_metrics.jsonl.gz): This file records the target definitions or target identifiers.

- [prediction_manifest.json](prediction_manifest.json): This file lists related records and their identifiers.

- [probability_reliability.csv](probability_reliability.csv): This file supports the calculation described in the parent guide.

- [ranked_seed_recovery.csv](ranked_seed_recovery.csv): This file records seed information or seed checks.

- [report_section_template.tex](report_section_template.tex): This file contains a LaTeX document or document section.

- [report_values.json](report_values.json): This file contains structured records from the parent calculation.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [scheduler_before_fast_node.log](scheduler_before_fast_node.log): This file contains saved program messages.

- [scheduler_before_storage_guard.log](scheduler_before_storage_guard.log): This file contains saved program messages.

- [status_before_fast_node.json](status_before_fast_node.json): This file records the execution state.

- [test_results.json](test_results.json): This file contains structured records from the parent calculation.

- [test_status.json](test_status.json): This file records the execution state.

- [training_history.csv](training_history.csv): This file records training progress or training inputs.

- [training_section_template.tex](training_section_template.tex): This file records training progress or training inputs.

- [validation.json](validation.json): This file records the completed validation checks.

## Child folders

- [archive_before_all_loops](archive_before_all_loops/README.md).

- [archive_before_expansion_250](archive_before_expansion_250/README.md).

- [figures](figures/README.md).

- [native_multiloop](native_multiloop/README.md).

- [predictions](predictions/README.md).
