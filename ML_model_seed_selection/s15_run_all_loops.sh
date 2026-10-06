#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedAllLoops
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/all_loops_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
python3 - <<'PY'
import json
from pathlib import Path
summary=json.loads(Path("integrals/higher_loops/integration_summary.json").read_text())
validation=json.loads(Path("integrals/higher_loops/validation.json").read_text())
assert summary["families"]==2100 and summary["targets"]==381272
assert validation["status"]=="passed" and len(validation["families"])==1100
PY
if [[ ! -f ML_model_seed_selection/runs/all_loops_latest.pt ]]; then
  .tools/seed-model/venv/bin/python ML_model_seed_selection/s12_prepare_features.py
fi
.tools/seed-model/venv/bin/python ML_model_seed_selection/s14_train_all_loops.py "$@"
