#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraTestReport
#$ -l h_rt=00:10:00,h_data=2G
#$ -j y
#$ -o ML_model_seed_selection/model_test/report_build.log
set -euo pipefail
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
make -C report
