#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraResidual
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
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
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s48_residual_run.py "$@"
