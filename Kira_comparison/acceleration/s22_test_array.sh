#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraAccelTest
#$ -t 1-24
#$ -tc 8
#$ -l h_rt=01:30:00,h_data=2G,h_vmem=3G
#$ -j y
#$ -o Kira_comparison/acceleration
index=$((SGE_TASK_ID-1))
case_id=$((index/2))
if ((index%2==0)); then batch_size=16; else batch_size=64; fi
exec bash Kira_comparison/acceleration/s08_run.sh --case "$case_id" --sizes "$batch_size" --partition test --stage results --repetitions 5 --policies frozen
