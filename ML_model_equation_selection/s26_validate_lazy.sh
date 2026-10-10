#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqLazyValidation
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
from pathlib import Path
import json
r=Path('ML_model_equation_selection')
s=json.loads((r/'validation/summary.json').read_text())
g=json.loads((r/'validation_grid.json').read_text())
assert s['all_exact'] and s['workflows']==5*3*len(g)
(r/'validation').rename(r/'validation_compact')
(r/'validation').mkdir()
PY
export KIRA_EQ_PARITY_VERSIONS=kira-compact,kira-lazy KIRA_EQ_PARITY_TAG=lazy_ KIRA_EQ_PARITY_REPORT=lazy_verification.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s14_check_fast.py
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-lazy
export KIRA_EQ_VALIDATION_GRID=ML_model_equation_selection/validation_grid.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py validate
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py validation
