#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitBuild
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s03_build.py
