#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelAudit
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s112_summarize_parallel.py confirmation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s117_check_parallel_application.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s115_audit_parallel.py
