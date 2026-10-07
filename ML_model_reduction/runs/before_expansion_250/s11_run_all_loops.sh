#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionAllLoops
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/runs/all_loops_scheduler.log
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
REDUCTION_PYTHON=.tools/seed-model/venv/bin/python
"$REDUCTION_PYTHON" ML_model_reduction/s02_prepare_data.py
"$REDUCTION_PYTHON" ML_model_reduction/s10_train_all_loops.py --resume
