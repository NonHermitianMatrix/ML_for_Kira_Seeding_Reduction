#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelPaper
#$ -l h_rt=00:08:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/report_build.log
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s31_plot.py
if [[ -f Kira_comparison/acceleration/expression_test_summary.json ]]; then
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py
fi
if [[ -f Kira_comparison/acceleration/expression_matched_summary.json ]]; then
 .tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py --matched
fi
make -C report
