#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostTree
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s08_train_tree.py
