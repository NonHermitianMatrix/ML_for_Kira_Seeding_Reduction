#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N ExpandedKira
#$ -l h_rt=00:30:00,h_data=2G
#$ -j y
#$ -o Expanded_Integrals/logs
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C PYTHONIOENCODING=utf-8
export FERMATPATH="$(pwd)/.tools/Ferl7/fer64"
ulimit -v 1843200
ulimit -f 524288
ulimit -c 0
timeout 1650s python3 Expanded_Integrals/s01_generate_family.py "$@"
