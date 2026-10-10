#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraEqCompactValidation
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
import sys,json
root=Path('ML_model_equation_selection')
sys.path.insert(0,str(root.resolve()))
from s10_summarize import aggregate,ratio
batches,rows=aggregate(root/'validation')
assert len(rows)==150 and all(r['success'] for r in rows)
keys=sorted({k for b in batches for k in b['methods']})
chosen=set()
for subset in [batches]+[[b for b in batches if b['topology']==t] for t in sorted({b['topology'] for b in batches})]:
 for prefix in ['learned:','distance:']:
  chosen.add(min((ratio(subset,k,'complete_seconds')['ratio'],k) for k in keys if k.startswith(prefix))[1])
grid=[['off',0]]+[[k.split(':')[0],float(k.split(':')[1])] for k in sorted(chosen)]
(root/'validation_grid.json').write_text(json.dumps(grid,indent=2)+'\n')
(root/'validation').rename(root/'validation_fast_features')
(root/'validation').mkdir()
print('Cached validation grid',grid,flush=True)
PY
export KIRA_EQ_PARITY_VERSIONS=kira-fast,kira-compact KIRA_EQ_PARITY_TAG=cached_ KIRA_EQ_PARITY_REPORT=cached_verification.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s14_check_fast.py
export KIRA_EQ_RUNTIME_BINARY=.tools/kira-equation-selection/kira-compact
export KIRA_EQ_VALIDATION_GRID=ML_model_equation_selection/validation_grid.json
.tools/seed-model/venv/bin/python ML_model_equation_selection/s04_experiment.py validate
.tools/seed-model/venv/bin/python ML_model_equation_selection/s10_summarize.py validation
