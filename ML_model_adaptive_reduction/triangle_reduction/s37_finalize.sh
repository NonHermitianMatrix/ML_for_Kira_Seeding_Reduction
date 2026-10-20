#!/bin/bash
#$ -cwd
#$ -q pod_short.q,pod_smp.q,campus2.q
#$ -S /bin/bash
#$ -N KiraTriangleReport
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 git/2.40.0 gmp/6.2.1 flint/2.8.0
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 65536
ulimit -c 0
for step in s17_analyze s18_plot s36_monitor_summary s40_equation_audit s19_write_report s22_guides s23_validate; do
 .tools/seed-model/venv/bin/python -u "ML_model_adaptive_reduction/triangle_reduction/${step}.py"
done
