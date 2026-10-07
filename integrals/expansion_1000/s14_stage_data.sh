#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraStageData
#$ -l h_rt=00:30:00,h_data=1G,h_vmem=4G
#$ -j y
#$ -o .tools/stage_expanded_data.log
set -euo pipefail
ulimit -v 1572864
ulimit -f 131072
ulimit -c 0
if (( $# )); then
  git -c gc.auto=0 add -A -- "$@"
else
  git -c gc.auto=0 add -A -- integrals
fi
git diff --cached --shortstat
