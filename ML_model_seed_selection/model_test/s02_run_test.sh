#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedTest
#$ -l h_rt=06:00:00,h_data=4G
#$ -j y
#$ -o ML_model_seed_selection/model_test/scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.tools/seed-model/matplotlib"
mkdir -p "$MPLCONFIGDIR"
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
timeout 21300s .tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s01_evaluate.py

.tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s03_plot_results.py
.tools/seed-model/venv/bin/python ML_model_seed_selection/model_test/s04_validate_outputs.py
