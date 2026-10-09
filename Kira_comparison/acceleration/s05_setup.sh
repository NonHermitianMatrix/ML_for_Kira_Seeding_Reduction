#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelSetup
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/setup.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s02_export_seed.py
python3 Kira_comparison/acceleration/s04_build.py
