#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraParallelReport
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
root=pathlib.Path.cwd();here=root/"Kira_comparison/integrated_runtime";exp=root/"Kira_comparison/parallel_inference"
sys.path.insert(0,str(here))
from s113_freeze_parallel import verify
from s03_records import retained
verify()
assert json.loads((exp/"verification.json").read_text())["all_passed"]
assert json.loads((exp/"confirmation_summary.json").read_text())["observed"]==640
assert json.loads((exp/"application_verification.json").read_text())["checks"]==8
active={n.findtext("JB_job_number") for n in ET.fromstring(subprocess.check_output(['/u/systems/UGE8.6.4/bin/lx-amd64/qstat', '-xml', '-u', 'rushil'])).iter("job_list")}
jobs=json.loads((root/".tools/kira-parallel-publication/jobs.json").read_text())
assert not active & {v for v in jobs.values() if isinstance(v,str)}
assert retained()<32*1024**2
from s105_parallel_records import retained as new_retained
assert new_retained()<12*1024**2
assert sum(p.stat().st_blocks*512 for p in (root/".tools/kira-parallel-inference").rglob("*") if p.is_file())<24*1024**2
for parent in [here,root/"ML_model_seed_selection/runtime_inference",root/"ML_model_reduction/runtime_training"]:
 for p in parent.glob("*.py"):ast.parse(p.read_text())
 for p in parent.glob("*.sh"):subprocess.run(["bash","-n",str(p)],check=True)
state=root/".tools/kira-parallel-publication/completion.json"
assert not state.exists()
state.write_text(json.dumps(dict(stage="comparisons_validated",all_declared_jobs_finished=True,published_blob_upper_bytes=66781184),indent=2)+"\n")
print("Final checks and resource limits verified",flush=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s122_document_parallel_readmes.py
.tools/seed-model/venv/bin/python .tools/kira-parallel-publication/s00_publish.py data
.tools/seed-model/venv/bin/python - <<'PY'
import json,subprocess
s=json.load(open(".tools/kira-parallel-publication/completion.json"))
subprocess.run([".tools/seed-model/venv/bin/python","Kira_comparison/integrated_runtime/s119_document_parallel.py","--data-commit",s["data_commit"]],check=True)
PY
.tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s120_plot_parallel.py
make -C report all
