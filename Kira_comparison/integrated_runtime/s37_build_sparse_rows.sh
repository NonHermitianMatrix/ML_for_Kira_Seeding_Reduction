#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSparseRowsBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s36_build_sparse_rows.py
KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-sparse KIRA_RUNTIME_HEADER=s10_sparse_policy.h KIRA_COST_BUILD_RECORD=sparse_rows_build.json KIRA_COST_PATCH=reduction_sparse_rows.patch python3 Kira_comparison/integrated_runtime/s00_build.py
