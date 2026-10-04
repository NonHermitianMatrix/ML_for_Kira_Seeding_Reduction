#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N IntegralLayout
#$ -l h_rt=00:20:00,h_data=2G
#$ -j y
#$ -o .tools/integrals-layout/logs
set -euo pipefail
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
timeout 1100s python3 integrals/s00_reorganize.py "$@"
