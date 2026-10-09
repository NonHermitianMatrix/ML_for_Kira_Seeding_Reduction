#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraFreeze
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/freeze.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage validation
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s20_freeze.py
bash Kira_comparison/acceleration/s08_run.sh --case 2 --stage combined_pilot --policies combined
bash Kira_comparison/acceleration/s08_run.sh --case 4 --stage combined_pilot --policies combined
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s13_audit.py --stage combined_pilot
.tools/seed-model/venv/bin/python -c 'import json; x=json.load(open("Kira_comparison/acceleration/combined_pilot_validation.json")); assert x["completed"]==2 and not x["incomplete"]'
submission=$("$SGE_ROOT/bin/lx-amd64/qsub" Kira_comparison/acceleration/s22_test_array.sh)
echo "$submission"
array_job=$(echo "$submission" | awk '{split($3,a,"."); print a[1]}')
"$SGE_ROOT/bin/lx-amd64/qsub" -hold_jid "$array_job" Kira_comparison/acceleration/s32_finalize.sh
