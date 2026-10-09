#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraLiveFull
#$ -t 1-7
#$ -tc 2
#$ -l h_rt=02:00:00,h_data=3G,h_vmem=4G
#$ -j y
#$ -o Kira_comparison/live_matrix
exec bash Kira_comparison/live_matrix/s06_run.sh --case "$((SGE_TASK_ID-1))"
