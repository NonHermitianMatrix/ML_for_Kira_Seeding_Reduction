#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedBuild
#$ -l h_rt=00:15:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
mkdir -p .tools/kira-shared-inference
g++ -std=c++17 -O3 -ffp-contract=off -fPIC -shared -static-libstdc++ -static-libgcc -Wl,--exclude-libs,ALL ML_model_seed_selection/runtime_inference/s11_shared_runtime.cpp -o .tools/kira-shared-inference/libseed.so
g++ -std=c++17 -O2 -I ML_model_reduction/runtime_training Kira_comparison/integrated_runtime/fast_evaluation/s00_check_pairs.cpp -o .tools/kira-shared-inference/check_pairs | tee Kira_comparison/integrated_runtime/fast_evaluation/row_feature_check.json
.tools/kira-shared-inference/check_pairs | tee Kira_comparison/integrated_runtime/fast_evaluation/row_feature_check.json
KIRA_RUNTIME_BUILD_DIR=.tools/kira-shared-inference KIRA_RUNTIME_HEADER=s16_shared_policy.h KIRA_COST_BUILD_RECORD=fast_evaluation/build.json KIRA_COST_PATCH=fast_evaluation/reduction_shared.patch python3 Kira_comparison/integrated_runtime/s00_build.py
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/fast_evaluation/s01_check_seed.py
