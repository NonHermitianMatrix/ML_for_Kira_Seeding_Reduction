#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedFixture
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/fixture_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s00_check_kira.py
