# extra 20 epochs

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

[s00_continue.py](s00_continue.py)

The program continues the published seed checkpoint for the requested twenty epochs.

The module defines these callable interfaces:

```python

def sha(p)
def write_status(stage, **more)
def main()

```

The imported external packages are `torch`.

The imported project modules are `s01_data`, `s03_train`.

These source constants locate inputs and outputs:

```python

WORK = pathlib.Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

torch.load(latest, map_location='cpu', weights_only=False)
torch.load(MODEL / 'trained_model.pt', map_location='cpu', weights_only=False)
(MODEL / 'README.md').read_text(encoding='utf-8')
(MODEL / 'README.md').write_text(text, encoding='utf-8')
torch.load(snapshot / 'trained_model.pt', map_location='cpu', weights_only=False)
torch.save(compact, temp)
torch.load(snapshot / 'runs/latest.pt', map_location='cpu', weights_only=False)

```

[s01_run.sh](s01_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedExtra20
#$ -l h_rt=24:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/extra_20_epochs/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
TRAIN_PYTHON=.tools/seed-model/venv/bin/python
"$TRAIN_PYTHON" - <<'PY'
import json,os,pathlib,platform,shutil,time
p=pathlib.Path("ML_model_seed_selection/runs/extra_20_epochs")
plan=json.loads((p/"request.json").read_text())
history=json.loads((p/"jobs.json").read_text()) if (p/"jobs.json").exists() else []
assert len(history)<plan["max_attempts"],"Continuation attempt limit reached"
assert shutil.disk_usage(".").free>2000000000,"Less than 2 GB free"
history.append(dict(job_id=os.environ.get("JOB_ID"),host=platform.node(),started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),cpu_slots=1,requested_memory_gib=4,virtual_memory_limit_kib=3145728))
(p/"jobs.json").write_text(json.dumps(history,indent=2)+"\n")
print(json.dumps(history[-1]),flush=True)
PY
if timeout --signal=TERM --kill-after=60s 82800s "$TRAIN_PYTHON" ML_model_seed_selection/runs/extra_20_epochs/s00_continue.py; then
  exit 0
else
  TRAIN_EXIT=$?
fi
if [[ "$TRAIN_EXIT" == 124 ]]; then
  "$TRAIN_PYTHON" - <<'PY'
import json,pathlib,subprocess,time
p=pathlib.Path("ML_model_seed_selection/runs/extra_20_epochs")
plan=json.loads((p/"request.json").read_text())
history=json.loads((p/"jobs.json").read_text())
assert len(history)<plan["max_attempts"],"Maximum automatic continuation attempts reached"
reply=subprocess.check_output(["qsub","ML_model_seed_selection/runs/extra_20_epochs/s01_run.sh"],text=True)
(p/"resubmission.json").write_text(json.dumps(dict(reason="bounded_walltime_reached",reply=reply,utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())),indent=2)+"\n")
print(reply,flush=True)
PY
  exit 0
fi
exit "$TRAIN_EXIT"

```

## Data and supporting files

- [jobs.json](jobs.json): This file contains structured records from the parent calculation.

- [launch.json](launch.json): This file contains structured records from the parent calculation.

- [preflight.json](preflight.json): This file contains structured records from the parent calculation.

- [request.json](request.json): This file contains structured records from the parent calculation.

- [run.lock](run.lock): This file supports the calculation described in the parent guide.

- [scheduler.log](scheduler.log): This file contains saved program messages.

- [setup_validation.json](setup_validation.json): This file contains structured records from the parent calculation.

- [status.json](status.json): This file records the execution state.
