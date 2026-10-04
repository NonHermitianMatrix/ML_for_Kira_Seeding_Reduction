#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCPUCheck
#$ -pe shared 4
#$ -l h_rt=00:15:00,h_data=2G
#$ -j y
#$ -o ML_model_seed_selection/runs/resource_check/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=4
ulimit -v 6291456
ulimit -f 32768
ulimit -c 0
timeout 780s .tools/seed-model/venv/bin/python ML_model_seed_selection/runs/resource_check/s00_cpu_scaling.py
