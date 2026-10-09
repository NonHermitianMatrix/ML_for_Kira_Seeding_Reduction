#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveAudit
#$ -l h_rt=00:45:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/live_matrix/audit.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s07_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s08_summarize.py
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s11_plot.py

