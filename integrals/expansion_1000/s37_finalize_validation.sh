#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraMathComplete
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
#$ -o integrals/expansion_1000/validation_combination.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s03_validate.py --pilot
.tools/seed-model/venv/bin/python integrals/expansion_1000/s36_combine_validation.py
