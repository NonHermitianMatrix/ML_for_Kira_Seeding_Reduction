#!/bin/bash
#$ -cwd
#$ -q pod_short.q,pod_smp.q,campus2.q
#$ -S /bin/bash
#$ -N KiraTriangleRepeat
#$ -l h_rt=00:20:00,h_data=8G,h_vmem=8G,arch=intel-gold*
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 git/2.40.0 gmp/6.2.1 flint/2.8.0
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 7340032
ulimit -f 65536
ulimit -c 0
.tools/seed-model/venv/bin/python -u ML_model_adaptive_reduction/triangle_reduction/s24_repeat_check.py
