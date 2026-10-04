#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedTrain
#$ -l h_rt=24:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
SEED_PYTHON=.tools/seed-model/venv/bin/python
"$SEED_PYTHON" ML_model_seed_selection/s09_check_training_inputs.py
if [[ -f ML_model_seed_selection/runs/latest.pt ]]; then
  timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s03_train.py --resume
else
  timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s03_train.py
fi
"$SEED_PYTHON" ML_model_seed_selection/s10_finalize_training.py
{
git -c gc.auto=0 add -- ML_model_seed_selection/trained_model.pt ML_model_seed_selection/trained_model.json ML_model_seed_selection/runs README.md ML_model_seed_selection/README.md
git -c gc.auto=0 commit -q -m 'Save seed-selection model after ten training epochs'
git -c pack.threads=1 -c pack.windowMemory=64m -c pack.deltaCacheSize=16m -c gc.auto=0 push origin main
} > .tools/seed-training/publish.log 2>&1
