#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostReady
#$ -l h_rt=00:15:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python ML_model_reduction/cost_training/s12_promote_tree.py
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s22_install_runtime.py
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s24_check_runtime.py
