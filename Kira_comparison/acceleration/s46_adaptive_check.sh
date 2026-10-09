#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAdaptCheck
#$ -l h_rt=00:45:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -c 0
export KIRA_ACCEL_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-accel-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_ACCEL_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage adaptive_pilot
.tools/seed-model/venv/bin/python - <<'CHECK'
import json
r=json.load(open('Kira_comparison/acceleration/adaptive_pilot_validation.json'))
assert r['passed'] and r['trials']==4 and r['completed']==4,r
CHECK
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s44_adaptive_run.py --partition train --case 4 --sizes 16 --policies trim_checked,pool_checked,adaptive_ml,adaptive_distance --stage adaptive_pilot
for kira_validation_case in 3 4; do
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s44_adaptive_run.py --partition validation --case "$kira_validation_case" --sizes 16 --policies trim_checked,pool_checked,adaptive_ml,adaptive_distance --stage adaptive_validation
done
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage adaptive_pilot
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage adaptive_validation
