#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraPublishTests
#$ -l h_rt=02:00:00,h_data=2G
#$ -j y
#$ -o integrals/expansion_1000/test_publication_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s12_finalize_tests.py
.tools/seed-model/venv/bin/python integrals/expansion_1000/s20_publish_release.py tests
