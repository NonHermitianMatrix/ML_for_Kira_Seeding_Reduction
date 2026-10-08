#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostAudit
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/finalization.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 32768
ulimit -c 0
.tools/seed-model/venv/bin/python Kira_comparison/s07_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/s08_summarize.py
.tools/seed-model/venv/bin/python Kira_comparison/s09_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/s13_native_audit.py
.tools/seed-model/venv/bin/python Kira_comparison/s15_native_summary.py
.tools/seed-model/venv/bin/python Kira_comparison/s16_native_plot.py
.tools/seed-model/venv/bin/python Kira_comparison/s23_cost_breakdown.py
python - <<'PY'
import json,pathlib
p=pathlib.Path('.tools/kira-comparison-publication/completion.json');x=json.loads(p.read_text());x['stage']='comparisons_validated';p.write_text(json.dumps(x,indent=2)+'\n')
print('Both comparisons validated and plotted')
PY
