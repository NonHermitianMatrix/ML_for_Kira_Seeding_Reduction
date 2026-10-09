#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraDevAudit
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/development_audit.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
for kira_development_stage in preflight_pilot adaptive_pilot adaptive_validation residual_pilot; do
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage "$kira_development_stage"
done
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s50_development_summary.py
