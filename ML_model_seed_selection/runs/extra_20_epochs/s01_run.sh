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
