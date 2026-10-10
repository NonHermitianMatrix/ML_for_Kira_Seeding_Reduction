#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostPilot
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_00_sunrise --policy stock --output Kira_comparison/multiloop_native/pilot_v3/sunrise_stock.json.gz
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_00_sunrise --policy collect --reference Kira_comparison/multiloop_native/pilot_v3/sunrise_stock.json.gz --output Kira_comparison/multiloop_native/pilot_v3/sunrise_collect.json.gz
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_02_double_box --policy stock --output Kira_comparison/multiloop_native/pilot_v3/box_stock.json.gz
.tools/seed-model/venv/bin/python Kira_comparison/multiloop_native/s02_run.py training_04_vacuum3 --policy stock --output Kira_comparison/multiloop_native/pilot_v3/vacuum_stock.json.gz
