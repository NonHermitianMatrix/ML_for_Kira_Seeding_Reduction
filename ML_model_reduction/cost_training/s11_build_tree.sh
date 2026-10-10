#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostTreeB
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_COST_BUILD_DIR=.tools/kira-cost-tree KIRA_COST_HEADER=s10_tree_policy.h
export KIRA_COST_BUILD_RECORD=tree_build.json KIRA_COST_PATCH=reduction_tree.patch
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s01_build.py
