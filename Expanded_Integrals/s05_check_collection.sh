#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N AuditKiraCollection
#$ -l h_rt=00:30:00,h_data=1G
#$ -j y
#$ -o Expanded_Integrals/logs/audit.log
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C PYTHONIOENCODING=utf-8
ulimit -v 786432
ulimit -f 131072
ulimit -c 0
timeout 1500s python3 Expanded_Integrals/s02_validate_collection.py
