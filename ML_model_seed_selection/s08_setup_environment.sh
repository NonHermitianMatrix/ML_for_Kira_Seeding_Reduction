#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraSeedEnv
#$ -l h_rt=00:20:00,h_data=3G
#$ -j y
#$ -o .tools/seed-model/logs
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2621440
ulimit -f 786432
ulimit -c 0
mkdir -p .tools/seed-model/tmp
export TMPDIR="$PWD/.tools/seed-model/tmp"
python3 -m venv --system-site-packages .tools/seed-model/venv
.tools/seed-model/venv/bin/python -m pip install --no-cache-dir --ignore-installed --no-deps --index-url https://download.pytorch.org/whl/cpu 'torch==2.2.2+cpu'
.tools/seed-model/venv/bin/python -c 'import torch,numpy;print("torch",torch.__version__,"numpy",numpy.__version__)'
