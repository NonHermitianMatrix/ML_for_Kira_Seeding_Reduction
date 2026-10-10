#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFinalAudit
#$ -l h_rt=01:00:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s53_summarize_reserved.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s66_summarize_cache.py
 .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s72_summarize_pair.py
if [ -f Kira_comparison/integrated_runtime/pair_freeze.json ]; then
 .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s76_summarize_pair_reserved.py
fi
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s30_verify.py
