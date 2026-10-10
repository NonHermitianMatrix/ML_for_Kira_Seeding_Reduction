#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraTempDBBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ulimit -c 0
python3 Kira_comparison/integrated_runtime/s27_build_ephemeral_db.py
