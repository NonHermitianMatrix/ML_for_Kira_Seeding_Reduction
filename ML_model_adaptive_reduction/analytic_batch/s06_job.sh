#!/bin/bash
#$ -cwd
#$ -q pod_short.q,pod_smp.q
#$ -S /bin/bash
#$ -N KiraBatchExact
#$ -l h_rt=02:00:00,h_data=8G,h_vmem=8G
#$ -pe shared 1
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 git/2.40.0
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 SYMPY_GROUND_TYPES=python OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 7340032
ulimit -c 0
.tools/seed-model/venv/bin/python -u "ML_model_adaptive_reduction/analytic_batch/$1" "${@:2}"
