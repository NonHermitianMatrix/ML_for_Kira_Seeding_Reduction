#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSeedPilot
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/kira_sufficiency_test/pilot_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
export KIRA_SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/kira-seed-${JOB_ID}.XXXXXX")
trap 'rm -rf -- "$KIRA_SCRATCH"' EXIT
.tools/seed-model/venv/bin/python ML_model_seed_selection/kira_sufficiency_test/s04_run_pilot.py
