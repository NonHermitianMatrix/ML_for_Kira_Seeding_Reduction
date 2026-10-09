#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExprMatch
#$ -l h_rt=00:50:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
index=$((SGE_TASK_ID-1))
case=$((index/2))
if (( index % 2 == 0 )); then size=1; else size=16; fi
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s89_matched_expression_run.py --partition test --case "$case" --sizes "$size" --repetitions 5 --policies expression_frozen --stage expression_matched
