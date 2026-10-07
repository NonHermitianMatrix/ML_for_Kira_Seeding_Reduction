#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpand250Par
#$ -pe shared 4
#$ -l h_rt=04:00:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_250/parallel_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"$GEN_PYTHON" integrals/expansion_250/s01_generate.py --loops 1 2 12 --profiles 101 102
"$GEN_PYTHON" integrals/expansion_250/s03_validate.py --pilot
"$GEN_PYTHON" integrals/expansion_250/s15_generate_parallel.py
"$GEN_PYTHON" integrals/expansion_250/s03_validate.py
