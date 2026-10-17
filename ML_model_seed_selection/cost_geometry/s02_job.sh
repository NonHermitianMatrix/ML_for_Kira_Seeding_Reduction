#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedCost
#$ -l h_rt=04:00:00,h_data=8G,h_vmem=8G
#$ -pe shared 1
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 7340032
ulimit -c 0
.tools/seed-model/venv/bin/python -u "ML_model_seed_selection/cost_geometry/$@"
