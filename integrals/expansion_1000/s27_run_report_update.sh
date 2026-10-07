#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraReportSources
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o integrals/expansion_1000/report_build.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6 git/2.40.0
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3145728
ulimit -f 131072
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import hashlib,json,re,subprocess,sys
from pathlib import Path
phase=Path("integrals/expansion_1000")
p=json.loads((phase/"publication.json").read_text())
assert p["training"]["status"]==p["tests"]["status"]=="pushed"
subprocess.run([sys.executable,str(phase/"s07_update_report.py"),"--data-commit",p["training"]["commit"],"--test-commit",p["tests"]["commit"]],check=True)
text=Path("report/report.tex").read_text()
abstract=re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",text,re.S).group(1)
assert hashlib.sha256(abstract.encode()).hexdigest()==json.loads((phase/"request.json").read_text())["abstract_sha256"]
PY
make -C report
