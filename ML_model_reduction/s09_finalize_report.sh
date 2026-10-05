#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionReport
#$ -l h_rt=00:30:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/runs/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/s06_check.py
.tools/seed-model/venv/bin/python ML_model_reduction/s08_finalize.py
make -C report
