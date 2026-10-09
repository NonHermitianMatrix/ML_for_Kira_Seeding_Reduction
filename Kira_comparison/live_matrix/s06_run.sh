#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveMatrix
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/live_matrix
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_LIVE_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-live-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_LIVE_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/live_matrix/s05_run.py "$@"

