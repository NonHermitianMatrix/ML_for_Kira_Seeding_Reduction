#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppPilot
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_pilot.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
bash Kira_comparison/acceleration/s08_run.sh --case 2 --stage cpp_pilot --policies row_cpp_native,row_cpp_audit
bash Kira_comparison/acceleration/s08_run.sh --case 4 --stage cpp_pilot --policies row_cpp_native,row_cpp_audit
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s29_cpp_audit.py
