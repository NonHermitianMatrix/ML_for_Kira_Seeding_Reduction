#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionSummary
#$ -l h_rt=06:00:00,h_data=10G
#$ -j y
#$ -o ML_model_reduction/model_test/finalize_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.tools/reduction-model/matplotlib"
mkdir -p "$MPLCONFIGDIR"
ulimit -v 8388608
ulimit -f 131072
ulimit -c 0
TEST_PYTHON=.tools/seed-model/venv/bin/python
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py --aggregate-only
"$TEST_PYTHON" ML_model_reduction/model_test/s05_validate_outputs.py
"$TEST_PYTHON" ML_model_reduction/model_test/s06_plot_results.py
"$TEST_PYTHON" - <<'PY'
import json
from pathlib import Path
p=Path("ML_model_reduction/model_test/parallel_execution.json")
r=json.loads(p.read_text());assert r["status"]=="workers_complete"
r["status"]="complete";r["aggregation_separate_memory_allocation"]=True
p.write_text(json.dumps(r,indent=2)+"\n")
PY
