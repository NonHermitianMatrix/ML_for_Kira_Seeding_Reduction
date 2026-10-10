#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelFreeze
#$ -l h_rt=00:20:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s112_summarize_parallel.py validation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s113_freeze_parallel.py
