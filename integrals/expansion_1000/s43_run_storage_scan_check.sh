#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraStorageScanCheck
#$ -l h_rt=00:15:00,h_data=1G,h_vmem=2G
#$ -j y
#$ -o integrals/expansion_1000/storage_scan_comparison.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s42_compare_storage_scans.py
