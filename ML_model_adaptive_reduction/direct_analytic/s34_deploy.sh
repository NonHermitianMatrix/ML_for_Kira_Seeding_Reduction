#!/bin/bash
#$ -cwd
#$ -q pod_short.q,pod_smp.q,campus2.q
#$ -S /bin/bash
#$ -N KiraDirectFinal
#$ -l h_rt=01:00:00,h_data=8G,h_vmem=8G
#$ -pe shared 2
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 git/2.40.0
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 SYMPY_GROUND_TYPES=python OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 7340032
ulimit -c 0
direct_python=.tools/seed-model/venv/bin/python
direct_folder=ML_model_adaptive_reduction/direct_analytic
"$direct_python" -u "$direct_folder/s35_import_check.py"
"$direct_python" -u "$direct_folder/s26_deploy_prepare.py"
"$direct_python" -u "$direct_folder/s27_deploy_test.py" 0 > "$direct_folder/logs/deploy0.log" 2>&1 &
pid0=$!
"$direct_python" -u "$direct_folder/s27_deploy_test.py" 1 > "$direct_folder/logs/deploy1.log" 2>&1 &
pid1=$!
status=0
wait "$pid0" || status=1
wait "$pid1" || status=1
if [ "$status" -ne 0 ]; then exit "$status"; fi
"$direct_python" -u "$direct_folder/s33_deploy_finish.py"
