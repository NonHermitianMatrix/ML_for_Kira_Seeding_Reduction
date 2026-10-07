#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReleaseComplete
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o .tools/final-release/publication.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
.tools/seed-model/venv/bin/python integrals/expansion_1000/s52_complete_release.py
