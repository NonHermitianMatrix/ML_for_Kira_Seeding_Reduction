#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraWorker
#$ -pe shared 2
#$ -l h_rt=02:00:00,h_data=2G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export KIRA_RUNTIME_SCRATCH=node
ulimit -v 2867200
ulimit -f 131072
ulimit -c 0
if [ "$#" -ne 1 ]; then
  echo 'Usage: qsub s17_application.sh REQUESTS.jsonl' >&2
  exit 2
fi
.tools/seed-model/venv/bin/python ML_model_workflow_selection/thread_policy/s15_worker.py < "$1"
