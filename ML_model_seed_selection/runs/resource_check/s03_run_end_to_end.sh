#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCPUCheck2
#$ -pe shared 2
#$ -l h_rt=00:15:00,h_data=2G
#$ -j y
#$ -o ML_model_seed_selection/runs/resource_check/end_to_end.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=2
ulimit -v 3145728
ulimit -f 32768
ulimit -c 0
timeout 780s .tools/seed-model/venv/bin/python ML_model_seed_selection/runs/resource_check/s02_end_to_end_scaling.py
