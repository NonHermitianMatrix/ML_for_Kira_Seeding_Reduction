#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParametric
#$ -l h_rt=04:00:00,h_data=4G,h_vmem=8G
#$ -pe shared 2
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 7340032
ulimit -c 0
if [[ "$1" == build ]]; then
  .tools/seed-model/venv/bin/python ML_model_adaptive_reduction/s22_build_parametric.py
  .tools/seed-model/venv/bin/python ML_model_adaptive_reduction/s24_parametric_runtime.py
else
  .tools/seed-model/venv/bin/python "ML_model_adaptive_reduction/$1"
fi
