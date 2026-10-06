#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionWeights
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o ML_model_reduction/model_test/checkpoint_validation.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_reduction/model_test/s09_validate_checkpoint.py
