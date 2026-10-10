#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraCostReport
#$ -l h_rt=00:10:00,h_data=2G,h_vmem=3G
#$ -j y
set -euo pipefail
export LC_ALL=C LANG=C OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
make -C report
