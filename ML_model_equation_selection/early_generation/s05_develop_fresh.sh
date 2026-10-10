#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEarlyDevelop
#$ -l h_rt=00:45:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/ML_model_equation_selection"
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s04_workflows.py collect
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s02_train.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/early_generation/s04_workflows.py pilot
