#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraCompressPilot
#$ -l h_rt=00:10:00,h_data=512M,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/compression_pilot.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,"integrals/expansion_1000")
from s28_compress_records import one_family,HERE,DATA,write,sha
p=DATA/"master_to_target/families/vacuum_L12_profile351"
first=one_family(p);digest=sha(p/"manifest.json")
second=one_family(p);assert first==second and digest==sha(p/"manifest.json")
assert not (p/".compression_pending.json").exists()
result=dict(status="passed",family=p.name,compression=first,idempotent=True,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
write(HERE/"compression_pilot.json",result)
print(json.dumps(result))
PY
