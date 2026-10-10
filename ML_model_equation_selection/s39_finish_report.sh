#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqFinishReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/s24_document.py --data-commit "${1:-main}"
.tools/seed-model/venv/bin/python ML_model_equation_selection/s38_plot.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s28_stratify.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s33_confirm_document.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s36_check_deployment.py
.tools/seed-model/venv/bin/python ML_model_equation_selection/s37_finish_documentation.py
make -C report all
