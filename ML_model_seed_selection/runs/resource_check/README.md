# resource check

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

[s00_cpu_scaling.py](s00_cpu_scaling.py)

The program measures CPU scaling using training records; never change production weights.

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

torch.load(str(HERE / 'runs/latest.pt'), map_location='cpu')
(out / 'cpu_scaling.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

```

[s01_run_cpu_scaling.sh](s01_run_cpu_scaling.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCPUCheck
#$ -pe shared 4
#$ -l h_rt=00:15:00,h_data=2G
#$ -j y
#$ -o ML_model_seed_selection/runs/resource_check/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=4
ulimit -v 6291456
ulimit -f 32768
ulimit -c 0
timeout 780s .tools/seed-model/venv/bin/python ML_model_seed_selection/runs/resource_check/s00_cpu_scaling.py

```

[s02_end_to_end_scaling.py](s02_end_to_end_scaling.py)

The program compares full training-input and gradient work with one and two CPU threads.

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s02_model`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

torch.load(str(HERE / 'runs/latest.pt'), map_location='cpu')
(HERE / 'runs/resource_check/end_to_end_scaling.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

```

[s03_run_end_to_end.sh](s03_run_end_to_end.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCPUCheck2
#$ -pe shared 2
#$ -l h_rt=00:15:00,h_data=2G
#$ -j y
#$ -o ML_model_seed_selection/runs/resource_check/end_to_end.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=2
ulimit -v 3145728
ulimit -f 32768
ulimit -c 0
timeout 780s .tools/seed-model/venv/bin/python ML_model_seed_selection/runs/resource_check/s02_end_to_end_scaling.py

```

## Data and supporting files

- [cpu_scaling.json](cpu_scaling.json): This file contains structured records from the parent calculation.

- [decision.json](decision.json): This file contains structured records from the parent calculation.

- [end_to_end.log](end_to_end.log): This file contains saved program messages.

- [end_to_end_scaling.json](end_to_end_scaling.json): This file contains structured records from the parent calculation.

- [scheduler.log](scheduler.log): This file contains saved program messages.
