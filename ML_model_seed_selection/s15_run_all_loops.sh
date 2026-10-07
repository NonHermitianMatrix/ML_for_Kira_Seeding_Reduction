#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedAllLoops
#$ -pe shared 4
#$ -l h_rt=12:00:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o ML_model_seed_selection/runs/expansion_1000_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
python3 - <<'PY'
import json
from pathlib import Path
assert json.loads(Path("integrals/expansion_1000/reader_validation.json").read_text())["status"]=="passed"
summary=json.loads(Path("integrals/expansion_1000/integration_summary.json").read_text())
validation=json.loads(Path("integrals/expansion_1000/validation.json").read_text())
assert summary["families"]==17100 and summary["targets"]==2301272
assert validation["status"]=="passed" and len(validation["families"])==12000
import hashlib
audit=json.loads(Path("integrals/validation_summary.json").read_text())
assert audit["status"]=="passed" and audit["family_count"]==17100
assert audit["catalog_sha256"]==hashlib.sha256(Path("integrals/catalog.json").read_bytes()).hexdigest()
assert audit["split_sha256"]==hashlib.sha256(Path("ML_model_seed_selection/split_manifest.json").read_bytes()).hexdigest()
PY
if [[ ! -f ML_model_seed_selection/runs/all_loops_latest.pt ]]; then
  .tools/seed-model/venv/bin/python ML_model_seed_selection/s12_prepare_features.py
fi
.tools/seed-model/venv/bin/python ML_model_seed_selection/s14_train_all_loops.py "$@"
