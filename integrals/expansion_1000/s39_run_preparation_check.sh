#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraPreparationCheck
#$ -pe shared 4
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=8G
#$ -j y
#$ -o integrals/expansion_1000/parallel_preparation_check.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s17_validate_readers.py
.tools/seed-model/venv/bin/python integrals/expansion_1000/s38_check_parallel_preparation.py
