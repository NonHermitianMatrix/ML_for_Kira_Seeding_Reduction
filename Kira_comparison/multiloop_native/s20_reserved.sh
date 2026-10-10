#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostTest
#$ -l h_rt=06:00:00,h_data=3G,h_vmem=4G
#$ -t 1-6
#$ -tc 3
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s19_reserved.py "$((SGE_TASK_ID-1))"
