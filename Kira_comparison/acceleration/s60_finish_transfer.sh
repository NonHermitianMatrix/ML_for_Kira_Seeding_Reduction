#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTransferDoc
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/transfer_finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s57_transfer_summary.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s58_transfer_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s59_transfer_report.py
