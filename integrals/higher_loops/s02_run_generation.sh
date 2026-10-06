#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraLoopGeneration
#$ -l h_rt=12:00:00,h_data=4G
#$ -j y
#$ -o integrals/higher_loops/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/higher_loops/s01_generate.py "$@"
