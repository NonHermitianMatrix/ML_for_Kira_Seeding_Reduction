#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCppBuild
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/cpp_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s24_export_cpp.py
python3 Kira_comparison/acceleration/s26_build_cpp.py
