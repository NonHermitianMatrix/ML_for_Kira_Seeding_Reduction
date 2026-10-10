#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraSharedReport
#$ -l h_rt=00:30:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load git/2.40.0 python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
ulimit -c 0
.tools/seed-model/venv/bin/python - <<'PY'
import ast,hashlib,json,pathlib,subprocess,sys,xml.etree.ElementTree as ET
root=pathlib.Path.cwd();here=root/"Kira_comparison/integrated_runtime";exp=here/"fast_evaluation"
sys.path.insert(0,str(here))
from s93_freeze_shared import verify
from s03_records import retained
verify()
assert json.loads((exp/"verification.json").read_text())["all_passed"]
assert json.loads((exp/"confirmation_summary.json").read_text())["observed"]==800
assert json.loads((exp/"application_verification.json").read_text())["checks"]==8
active={n.findtext("JB_job_number") for n in ET.fromstring(subprocess.check_output(['/u/systems/UGE8.6.4/bin/lx-amd64/qstat', '-xml', '-u', 'rushil'])).iter("job_list")}
assert not active & {"15120808","15120815","15120819","15120827","15120864"}
assert retained()<32*1024**2
assert sum(p.stat().st_blocks*512 for p in (root/".tools/kira-shared-inference").rglob("*") if p.is_file())<16*1024**2
for parent in [here,root/"ML_model_seed_selection/runtime_inference",root/"ML_model_reduction/runtime_training"]:
 for p in parent.glob("*.py"):ast.parse(p.read_text())
 for p in parent.glob("*.sh"):subprocess.run(["bash","-n",str(p)],check=True)
state=root/".tools/kira-shared-publication/completion.json"
assert not state.exists()
state.write_text(json.dumps(dict(stage="comparisons_validated",all_declared_jobs_finished=True,published_blob_upper_bytes=44470272),indent=2)+"\n")
print("Final checks and resource limits verified",flush=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s103_document_shared_readmes.py
.tools/seed-model/venv/bin/python .tools/kira-shared-publication/s00_publish.py data
.tools/seed-model/venv/bin/python - <<'PY'
import json,subprocess
s=json.load(open(".tools/kira-shared-publication/completion.json"))
subprocess.run([".tools/seed-model/venv/bin/python","Kira_comparison/integrated_runtime/s99_document_shared.py","--data-commit",s["data_commit"]],check=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s100_plot_shared.py
make -C report all
