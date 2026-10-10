#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFastRowsBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_RUNTIME_HEADER=s07_fast_policy.h KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-fast
export KIRA_COST_BUILD_RECORD=fast_rows_build.json KIRA_COST_PATCH=reduction_fast_rows.patch
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py
