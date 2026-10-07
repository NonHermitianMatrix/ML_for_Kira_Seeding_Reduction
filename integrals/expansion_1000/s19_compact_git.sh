#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraGitCompact
#$ -l h_rt=01:00:00,h_data=2G
#$ -j y
#$ -o integrals/expansion_1000/git_compaction.log
set -euo pipefail
export LC_ALL=C
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
git rev-parse HEAD > integrals/expansion_1000/git_head_before_compaction.txt
git count-objects -v
git -c pack.threads=1 -c pack.windowMemory=64m -c pack.deltaCacheSize=16m -c pack.packSizeLimit=256m -c gc.auto=0 repack -a -d
git count-objects -v
test "$(git rev-parse HEAD)" = "$(cat integrals/expansion_1000/git_head_before_compaction.txt)"
