#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraGenFinish
#$ -l h_rt=00:30:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=.tools/seed-model/venv/bin/python
D=Kira_comparison/generalization
$P $D/s04_optimal_paths.py
$P $D/s05_verify_certificates.py
$P $D/s08_analyze.py
