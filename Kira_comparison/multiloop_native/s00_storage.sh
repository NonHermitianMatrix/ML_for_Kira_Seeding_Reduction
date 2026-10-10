#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraStorage
#$ -l h_rt=00:20:00,h_data=1G,h_vmem=2G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C
python - <<'PY'
import json,subprocess,time
from pathlib import Path
p=Path('Kira_comparison/multiloop_native/storage_audit.json')
begin=time.time()
r=subprocess.run(['du','-s','-B1','.'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=1000)
out=dict(elapsed_seconds=time.time()-begin,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr[-3000:],local_observed_bytes=262680576,local_allowance_bytes=400000000)
if r.returncode==0:out['cluster_allocated_bytes']=int(r.stdout.split()[0])
p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
PY
