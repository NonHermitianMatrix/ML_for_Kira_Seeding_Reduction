#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraOrder
#$ -l h_rt=03:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export KIRA_RUNTIME_SCRATCH=node
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python "ML_model_workflow_selection/ordering_policy/${1:-s04_probe.py}" "${@:2}"
