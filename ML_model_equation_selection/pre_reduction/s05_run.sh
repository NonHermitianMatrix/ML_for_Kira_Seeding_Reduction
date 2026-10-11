#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPreFull
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s04_check.py kernel
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s02_study.py validation
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s02_study.py freeze
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s02_study.py test
.tools/seed-model/venv/bin/python ML_model_equation_selection/pre_reduction/s04_check.py integration
.tools/seed-model/venv/bin/python -u ML_model_equation_selection/pre_reduction/s04_check.py audit
