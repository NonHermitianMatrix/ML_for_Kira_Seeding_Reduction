#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitReport
#$ -l h_rt=00:08:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s14_report.py --data-commit "$1"
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s20_report_finish.py --data-commit "$1"
make -C report
