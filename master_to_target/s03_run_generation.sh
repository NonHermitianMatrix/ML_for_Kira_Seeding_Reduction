#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N MasterToTarget
#$ -l h_rt=01:00:00,h_data=4G
#$ -o master_to_target/logs/generation.log
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C
ulimit -v 3670016
ulimit -f 131072
ulimit -c 0
timeout 2700s python3 master_to_target/s01_generate_targets.py "$@"
if [ "$#" -eq 0 ]; then
    timeout 1800s python3 master_to_target/s02_validate_targets.py --require-all
else
    timeout 1800s python3 master_to_target/s02_validate_targets.py
fi
