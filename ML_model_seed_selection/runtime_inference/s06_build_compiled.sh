#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedCppBuild
#$ -l h_rt=00:10:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 1572864
ulimit -c 0
mkdir -p .tools/kira-seed-inference
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s03_export_compiled.py
g++ -std=c++17 -O3 -ffp-contract=off -fPIC -shared -static-libstdc++ -static-libgcc -Wl,--exclude-libs,ALL ML_model_seed_selection/runtime_inference/s02_seed_runtime.cpp -o .tools/kira-seed-inference/libseed.so
.tools/seed-model/venv/bin/python ML_model_seed_selection/runtime_inference/s05_verify_compiled.py
