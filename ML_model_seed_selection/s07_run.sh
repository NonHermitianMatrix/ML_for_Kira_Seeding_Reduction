#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedModel
#$ -l h_rt=24:00:00,h_data=4G
#$ -j y
#$ -o .tools/seed-model/logs
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
SEED_PYTHON=.tools/seed-model/venv/bin/python
MODE=check
if (( $# )); then MODE="$1"; fi
case "$MODE" in
  prepare) timeout 1100s "$SEED_PYTHON" ML_model_seed_selection/s00_prepare_data.py ;;
  check) timeout 600s "$SEED_PYTHON" ML_model_seed_selection/s06_check.py ;;
  train) shift; timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s03_train.py "$@" ;;
  evaluate) shift; timeout 82800s "$SEED_PYTHON" ML_model_seed_selection/s05_evaluate.py "$@" ;;
  *) echo "Use prepare, check, train or evaluate." >&2; exit 2 ;;
esac
