#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppCheck
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_check.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s29_cpp_audit.py --stage cpp_pilot_v3
