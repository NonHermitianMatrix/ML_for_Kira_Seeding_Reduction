#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTestReport
#$ -l h_rt=02:00:00,h_data=4G
#$ -j y
#$ -o ML_model_reduction/model_test/finalize.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
TEST_PYTHON=.tools/seed-model/venv/bin/python
"$TEST_PYTHON" ML_model_reduction/model_test/s09_validate_checkpoint.py
"$TEST_PYTHON" ML_model_reduction/model_test/s05_validate_outputs.py
"$TEST_PYTHON" ML_model_reduction/model_test/s06_plot_results.py
"$TEST_PYTHON" ML_model_reduction/model_test/s07_update_report.py
make -C report
"$TEST_PYTHON" ML_model_reduction/model_test/s07_update_report.py --validate-build
