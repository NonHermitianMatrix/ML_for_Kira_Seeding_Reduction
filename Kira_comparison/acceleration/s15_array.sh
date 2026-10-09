#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelArray
#$ -t 1-6
#$ -tc 2
#$ -l h_rt=00:40:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
exec bash Kira_comparison/acceleration/s08_run.sh --case "$((SGE_TASK_ID-1))" "$@"
