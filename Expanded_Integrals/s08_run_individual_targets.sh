#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N IndividualTargets
#$ -l h_rt=00:10:00,h_data=2G
#$ -j y
#$ -o Expanded_Integrals/logs
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C PYTHONIOENCODING=utf-8
ulimit -v 1843200
ulimit -f 65536
ulimit -c 0
timeout 540s python3 Expanded_Integrals/s07_add_individual_targets.py
