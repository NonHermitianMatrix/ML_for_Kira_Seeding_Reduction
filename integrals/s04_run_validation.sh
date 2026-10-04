#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N CheckIntegralLayout
#$ -l h_rt=00:25:00,h_data=2G
#$ -j y
#$ -o .tools/integrals-layout/logs
set -euo pipefail
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
timeout 1400s python3 integrals/s02_validate.py "$@"
