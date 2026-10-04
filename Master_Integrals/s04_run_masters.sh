#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraMasterBases
#$ -l h_rt=00:45:00,h_data=4G
#$ -o Master_Integrals/logs/masters.log
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
export FERMATPATH="$(pwd)/.tools/Ferl7/fer64"
ulimit -v 3670016
ulimit -f 1048576
ulimit -c 0
python3 Master_Integrals/s02_generate_masters.py "$@"
if [ "$#" -eq 0 ]; then
    python3 Master_Integrals/s03_validate_catalog.py --require-all
else
    python3 Master_Integrals/s03_validate_catalog.py
fi
