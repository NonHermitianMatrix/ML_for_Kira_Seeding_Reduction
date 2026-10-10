#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqTest
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-lazy
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s12_freeze.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py test
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py model_test
.tools/seed-model/venv/bin/python ML_model_equation_selection/s17_audit.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s18_additional_checks.py
