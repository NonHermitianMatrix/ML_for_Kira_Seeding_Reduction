#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitTest
#$ -l h_rt=01:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_FAST_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-fast-${JOB_ID}-${SGE_TASK_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_FAST_SCRATCH"' EXIT
index=$((SGE_TASK_ID-1)); case=$((index/2))
if (( index % 2 == 0 )); then size=1; else size=16; fi
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s06_run.py --partition test --case "$case" --size "$size" --repetitions 5
