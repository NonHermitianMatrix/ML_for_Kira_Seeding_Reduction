#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitRelease
#$ -l h_rt=00:08:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s18_release.py
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s16_document.py
python - <<'PY'
from pathlib import Path
import json
p=Path('.tools/kira-fast-publication/completion.json')
assert not p.exists()
p.write_text(json.dumps(dict(stage="comparisons_validated",expected_trials=480,declared_records=492,published_blob_upper_bytes=0,prior_commit="99ccf5b6bf4bc1beab307cddf684c40d5ab19e5d"),indent=2)+"\n")
print("Ready for code/data publication and report rendering.")
PY
