#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraPublishTests
#$ -l h_rt=06:00:00,h_data=2G
#$ -j y
#$ -o integrals/expansion_1000/test_publication_scheduler.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
python3 - <<'CACHE'
import json
from pathlib import Path
assert json.loads(Path("integrals/expansion_1000/git_cache_refresh.json").read_text())["status"]=="verified_partial_git_cache_active"
CACHE
.tools/seed-model/venv/bin/python integrals/expansion_1000/s12_finalize_tests.py
.tools/seed-model/venv/bin/python integrals/expansion_1000/s20_publish_release.py tests
