#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExactFinal
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=ML_model_equation_selection/exact_backend
test ! -e "$P/reader_final_freeze.json"
.tools/seed-model/venv/bin/python "$P/s16_reader_study.py" prepare
.tools/seed-model/venv/bin/python "$P/s16_reader_study.py" freeze
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" test
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" streams
.tools/seed-model/venv/bin/python "$P/s18_reader_audit.py"
.tools/seed-model/venv/bin/python "$P/s19_reader_analyze.py"
.tools/seed-model/venv/bin/python "$P/s20_reader_plot.py"
