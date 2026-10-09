#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprAudit
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/expression_finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_pilot
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_thresholds
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_preflight
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_small
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s68_expression_audit.py --stage expression_validation
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s76_expression_summary.py
