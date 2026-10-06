#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraExpandedReport
#$ -l h_rt=00:20:00,h_data=2G,h_vmem=4G
#$ -j y
#$ -o ML_model_reduction/model_test/finalize.log
set -euo pipefail
# Current combined report: requires --data-commit and --test-commit.
exec bash integrals/higher_loops/s13_build_report.sh "$@"
