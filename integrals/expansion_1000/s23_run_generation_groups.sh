#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandGroups
#$ -l h_rt=06:00:00,h_data=512M,h_vmem=4G
#$ -pe shared 4
#$ -t 1-3
#$ -tc 3
#$ -j y
#$ -o integrals/expansion_1000/
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"${GEN_PYTHON}" integrals/expansion_1000/s22_generate_group.py
