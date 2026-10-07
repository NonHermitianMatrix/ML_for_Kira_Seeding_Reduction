#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandMathCheck
#$ -l h_rt=01:00:00,h_data=1G,h_vmem=16G
#$ -pe shared 12
#$ -j y
#$ -o integrals/expansion_1000/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"${GEN_PYTHON}" integrals/expansion_1000/s24_combine_groups.py
"${GEN_PYTHON}" integrals/expansion_1000/s03_validate.py --pilot
"${GEN_PYTHON}" integrals/expansion_1000/s03_validate.py
