#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraAllLoopData
#$ -l h_rt=02:00:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o integrals/higher_loops/full_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
GEN_PYTHON=.tools/seed-model/venv/bin/python
"$GEN_PYTHON" integrals/higher_loops/s01_generate.py --loops 2 12 --profiles 1 3
"$GEN_PYTHON" integrals/higher_loops/s03_validate.py --pilot
"$GEN_PYTHON" integrals/higher_loops/s01_generate.py
"$GEN_PYTHON" integrals/higher_loops/s03_validate.py
"$GEN_PYTHON" integrals/higher_loops/s05_integrate.py
