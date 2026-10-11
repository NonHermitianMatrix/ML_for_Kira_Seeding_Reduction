#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExactStudy
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=ML_model_equation_selection/exact_backend
if [ "$1" = build ]; then
 mkdir -p "$P/build" "$P/development"
 g++ -O3 -std=c++11 -fPIC -shared "$P/s01_transform.cpp" -lgmpxx -lgmp -o "$P/build/transform.so"
 .tools/seed-model/venv/bin/python - <<'PY'
import ctypes,json,hashlib,subprocess
from pathlib import Path
p=Path('ML_model_equation_selection/exact_backend')
lib=ctypes.CDLL('libgmp.so.10')
d=dict(compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
 gmp_version=ctypes.c_char_p.in_dll(lib,'__gmp_version').value.decode(),
 source_sha256=hashlib.sha256((p/'s01_transform.cpp').read_bytes()).hexdigest(),
 library_sha256=hashlib.sha256((p/'build/transform.so').read_bytes()).hexdigest(),
 command='g++ -O3 -std=c++11 -fPIC -shared s01_transform.cpp -lgmpxx -lgmp -o build/transform.so')
(p/'build/build.json').write_text(json.dumps(d,indent=2)+'\n')
print(d,flush=True)
PY
 .tools/seed-model/venv/bin/python "$P/s04_check.py" kernel
else
 test ! -e "$P/freeze.json"
 .tools/seed-model/venv/bin/python "$P/s05_study.py" prepare
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" labels
 .tools/seed-model/venv/bin/python "$P/s05_study.py" train
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" validation
 .tools/seed-model/venv/bin/python "$P/s05_study.py" freeze
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" test
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" streams
 .tools/seed-model/venv/bin/python "$P/s04_check.py" integration
fi
