#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTempDBCheck
#$ -l h_rt=00:05:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 1572864
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s32_test_database_guard.py
