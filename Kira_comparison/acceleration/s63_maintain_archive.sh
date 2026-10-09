#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraArchive
#$ -l h_rt=01:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration/archive_monitor.log
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
ulimit -v 786432
.tools/seed-model/venv/bin/python - <<'MONITOR'
import pathlib,subprocess,time
h=pathlib.Path('Kira_comparison/acceleration')
for iteration in range(180):
 subprocess.run(['.tools/seed-model/venv/bin/python',str(h/'s61_evidence_archive.py'),'--min-age','10'],check=True)
 if len(list((h/'results').glob('*.json.gz')))==720 and len(list((h/'transfer_test').glob('*.json.gz')))==60:
  subprocess.run(['.tools/seed-model/venv/bin/python',str(h/'s61_evidence_archive.py'),'--min-age','0'],check=True)
  break
 time.sleep(20)
MONITOR
