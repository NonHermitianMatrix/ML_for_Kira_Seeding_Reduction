#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraNativeResume
#$ -t 1-7
#$ -tc 2
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/native_seed/results
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COMPARISON_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-cost-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_COMPARISON_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/s24_resume_native.py --case "$((SGE_TASK_ID-1))"
