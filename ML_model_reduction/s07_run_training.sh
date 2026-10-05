#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTrain
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/runs/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
REDUCTION_PYTHON=.tools/seed-model/venv/bin/python
"$REDUCTION_PYTHON" ML_model_reduction/s06_check.py
"$REDUCTION_PYTHON" ML_model_reduction/s02_prepare_data.py
"$REDUCTION_PYTHON" ML_model_reduction/s04_train.py --resume
