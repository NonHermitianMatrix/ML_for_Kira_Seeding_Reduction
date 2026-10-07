#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpand1000Par
#$ -pe shared 12
#$ -l h_rt=08:00:00,h_data=512M,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/parallel_12_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"$GEN_PYTHON" integrals/expansion_1000/s01_generate.py --loops 1 2 12 --profiles 351 352
"$GEN_PYTHON" integrals/expansion_1000/s03_validate.py --pilot
"$GEN_PYTHON" integrals/expansion_1000/s15_generate_parallel.py
"$GEN_PYTHON" integrals/expansion_1000/s03_validate.py
