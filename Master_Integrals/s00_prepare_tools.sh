#!/bin/bash
# Run from the project root on Hoffman before submitting s01_build_kira.sh.
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
KIRA_PROJECT="$(pwd)"
test -f "$KIRA_PROJECT/rules.md"
ulimit -v 1572864
ulimit -f 1048576
ulimit -c 0
python3 - <<'PYCHECK'
import subprocess
used=int(subprocess.check_output(['du','-sb','.']).split()[0])
if used > 7_000_000_000:
    raise SystemExit('Insufficient project storage headroom for the build')
PYCHECK
mkdir -p .tools/downloads Master_Integrals/logs
python3 -m pip install --disable-pip-version-check --no-cache-dir --upgrade --target .tools/build-python meson==1.7.2 ninja==1.11.1.3
if [ ! -d .tools/kira-source/.git ]; then
    git clone --depth 1 --branch 3.1 https://gitlab.com/kira-pyred/kira.git .tools/kira-source
fi
test "$(git --git-dir=.tools/kira-source/.git rev-parse HEAD)" = 5760f42f8decd7eb5474c780db75b5e5e7b450a0
curl -fL --max-time 60 --max-filesize 67108864 -o .tools/downloads/yaml-cpp-0.7.0.tar.gz https://codeload.github.com/jbeder/yaml-cpp/tar.gz/refs/tags/yaml-cpp-0.7.0
curl -fL --max-time 60 --max-filesize 67108864 -o .tools/downloads/Ferl7.tar.gz https://home.bway.net/lewis/fermat64/Ferl7.tar.gz
printf '%s  %s\n' 43e6a9fcb146ad871515f0d0873947e5d497a1c9c60c58cb102a97b47208b7c3 .tools/downloads/yaml-cpp-0.7.0.tar.gz | sha256sum -c -
printf '%s  %s\n' 67954cc4cbc6e96b8a2080e142e0ce7cad05d1036edc928e6600de47888a606c .tools/downloads/Ferl7.tar.gz | sha256sum -c -
