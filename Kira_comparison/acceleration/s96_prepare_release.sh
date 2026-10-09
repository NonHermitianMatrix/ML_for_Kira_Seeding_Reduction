#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReleaseDocs
#$ -l h_rt=00:12:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/release_documents.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export LC_ALL=C LANG=C PYTHONIOENCODING=utf-8
ulimit -v 2097152
ulimit -f 131072
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s85_expression_report.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s94_matched_expression_report.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s35_document.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s86_finish_documentation.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s31_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s87_expression_plot.py --matched
.tools/seed-model/venv/bin/python Kira_comparison/acceleration/s95_release_checks.py
