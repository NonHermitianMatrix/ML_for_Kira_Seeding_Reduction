#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraModularBuild
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
g++ -std=c++17 -O2 ML_model_reduction/runtime_training/s03_test_features.cpp -o .tools/kira-runtime-modular/feature_test
.tools/seed-model/venv/bin/python ML_model_reduction/runtime_training/s04_test_features.py
export KIRA_RUNTIME_HEADER=s02_modular_policy.h KIRA_RUNTIME_BUILD_DIR=.tools/kira-runtime-modular
export KIRA_COST_BUILD_RECORD=modular_build.json KIRA_COST_PATCH=reduction_modular.patch
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s00_build.py
