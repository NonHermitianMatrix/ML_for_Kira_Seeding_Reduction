#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedTest
#$ -l h_rt=02:00:00,h_data=4G
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
timeout 6900s .tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s01_evaluate.py

.tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s03_plot_results.py
.tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s04_validate_outputs.py
