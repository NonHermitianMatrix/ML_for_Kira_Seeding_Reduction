#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelBuild
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
mkdir -p .tools/kira-parallel-inference
g++ -std=c++17 -O3 -ffp-contract=off -fopt-info-vec-optimized=.tools/kira-parallel-inference/vectorization.log -fPIC -shared -static-libstdc++ -static-libgcc -Wl,--exclude-libs,ALL ML_model_seed_selection/runtime_inference/s13_lane_runtime.cpp -o .tools/kira-parallel-inference/libseed.so
g++ -std=c++17 -O2 -I ML_model_reduction/runtime_training Kira_comparison/parallel_inference/s00_check_arithmetic.cpp -o .tools/kira-parallel-inference/check_arithmetic
.tools/kira-parallel-inference/check_arithmetic | tee Kira_comparison/parallel_inference/arithmetic_check.json
.tools/seed-model/venv/bin/python Kira_comparison/parallel_inference/s01_check_seed.py
KIRA_RUNTIME_BUILD_DIR=.tools/kira-parallel-inference KIRA_RUNTIME_HEADER=s20_literal_policy.h KIRA_COST_BUILD_RECORD=../parallel_inference/build.json KIRA_COST_PATCH=../parallel_inference/reduction_parallel.patch python3 Kira_comparison/integrated_runtime/s00_build.py
