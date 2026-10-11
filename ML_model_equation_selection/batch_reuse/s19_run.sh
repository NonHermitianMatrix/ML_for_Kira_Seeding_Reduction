#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraBatchNative
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 gcc/9.5.0
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s14_pack_analyze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s15_integration.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s16_native.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s18_native_study.py prepare
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s18_native_study.py validation
.tools/seed-model/venv/bin/python ML_model_equation_selection/batch_reuse/s18_native_study.py freeze
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/batch_reuse/s18_native_study.py test
