#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExitFreeze
#$ -l h_rt=00:05:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.tools/seed-model/venv/bin/python Kira_comparison/fast_expression/s08_freeze.py
QSUB_FAST="${SGE_ROOT:-/u/systems/UGE8.6.4}/bin/${SGE_ARCH:-lx-amd64}/qsub"
TEST_FAST=$("$QSUB_FAST" -terse -t 1-24 -tc 2 -o .tools/kira-fast-expression Kira_comparison/fast_expression/s09_test_array.sh)
CHECK_FAST=$("$QSUB_FAST" -terse -hold_jid "${TEST_FAST%%.*}" -o .tools/kira-fast-expression/test_check.log Kira_comparison/fast_expression/s12_check.sh test)
python - "$TEST_FAST" "$CHECK_FAST" <<'PY'
import json,pathlib,sys,datetime
pathlib.Path('Kira_comparison/fast_expression/execution.json').write_text(json.dumps(dict(test_job=sys.argv[1],audit_job=sys.argv[2],concurrency=2,submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
print(sys.argv[1:])
PY
