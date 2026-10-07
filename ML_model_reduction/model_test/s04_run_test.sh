#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraReductionTest
#$ -l h_rt=06:00:00,h_data=2G,h_vmem=4G
#$ -pe shared 4
#$ -j y
#$ -o ML_model_reduction/model_test/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
python3 - <<'GATE'
import json
from pathlib import Path
p=Path("integrals/expansion_1000/publication.json")
r=json.loads(p.read_text());assert r["training"]["status"]=="pushed"
assert json.loads(Path("integrals/expansion_1000/training_release.json").read_text())["status"]=="both_models_validated"
GATE
TEST_PYTHON=.tools/seed-model/venv/bin/python
if [[ "${1:-}" == "--plots-only" ]]; then
  "$TEST_PYTHON" ML_model_reduction/model_test/s06_plot_results.py
  exit 0
fi
"$TEST_PYTHON" ML_model_reduction/model_test/s03_check_metrics.py
"$TEST_PYTHON" ML_model_reduction/model_test/s02_evaluate.py --limit 2
"$TEST_PYTHON" ML_model_reduction/model_test/s10_parallel_test.py --workers-only

# Complete aggregation, output checks and plots with s12_finalize_test.sh.
