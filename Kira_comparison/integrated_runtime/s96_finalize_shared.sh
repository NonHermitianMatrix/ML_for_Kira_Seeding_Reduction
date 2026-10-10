#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedAudit
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s92_summarize_shared.py confirmation
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s98_check_shared_application.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s95_audit_shared.py
