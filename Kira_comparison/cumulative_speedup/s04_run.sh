#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCumulative
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
PYTHON=.tools/seed-model/venv/bin/python
BASE=Kira_comparison/cumulative_speedup
if [ "$1" = "prepare" ]; then
 "$PYTHON" "$BASE/s01_cases.py"
 "$PYTHON" "$BASE/s03_study.py" pilot
elif [ "$1" = "pipeline" ]; then
 "$PYTHON" "$BASE/s03_study.py" freeze
 "$PYTHON" "$BASE/s10_parallel.py"
 bash "$BASE/s09_finish.sh"
else
 "$PYTHON" "$BASE/s03_study.py" "$1"
fi
