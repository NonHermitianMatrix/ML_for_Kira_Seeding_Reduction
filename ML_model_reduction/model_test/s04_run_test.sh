#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTest
#$ -l h_rt=02:00:00,h_data=4G
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
TEST_PYTHON=.tools/seed-model/venv/bin/python
"$TEST_PYTHON" ML_model_reduction/model_test/s03_check_metrics.py
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py --limit 2
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py
