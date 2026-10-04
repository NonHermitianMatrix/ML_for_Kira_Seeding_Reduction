#!/bin/bash
#$ -cwd
#$ -S /bin/bash
#$ -N KiraMastersBuild
#$ -l h_rt=00:30:00,h_data=4G
#$ -o Master_Integrals/logs/build.log
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load gcc/9.5.0 python/3.9.6 cmake/3.19.5
KIRA_PROJECT="$(pwd)"
export PYTHONPATH="$KIRA_PROJECT/.tools/build-python"
export PATH="$KIRA_PROJECT/.tools/build-python/bin:$PATH"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export CC=gcc CXX=g++
export CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0"
ulimit -v 3670016
ulimit -f 1048576
ulimit -c 0
test -f .tools/kira-source/meson.build
python3 - <<'PYCHECK'
import subprocess
used=int(subprocess.check_output(['du','-sb','.']).split()[0])
if used > 7_000_000_000:
    raise SystemExit('Insufficient project storage headroom for the build')
PYCHECK
printf '%s  %s\n' 67954cc4cbc6e96b8a2080e142e0ce7cad05d1036edc928e6600de47888a606c .tools/downloads/Ferl7.tar.gz | sha256sum -c -
printf '%s  %s\n' 43e6a9fcb146ad871515f0d0873947e5d497a1c9c60c58cb102a97b47208b7c3 .tools/downloads/yaml-cpp-0.7.0.tar.gz | sha256sum -c -
tar -xzf .tools/downloads/yaml-cpp-0.7.0.tar.gz -C .tools
tar -xzf .tools/downloads/Ferl7.tar.gz -C .tools
cmake -S .tools/yaml-cpp-yaml-cpp-0.7.0 -B .tools/yaml-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$KIRA_PROJECT/.tools/kira-deps" -DCMAKE_INSTALL_LIBDIR=lib -DYAML_CPP_BUILD_TESTS=OFF -DYAML_CPP_BUILD_TOOLS=OFF -DYAML_BUILD_SHARED_LIBS=OFF
cmake --build .tools/yaml-build --parallel 1
cmake --install .tools/yaml-build
export PKG_CONFIG_PATH="$KIRA_PROJECT/.tools/kira-deps/share/pkgconfig:$KIRA_PROJECT/.tools/kira-deps/lib64/pkgconfig:$KIRA_PROJECT/.tools/kira-deps/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
export CMAKE_PREFIX_PATH="$KIRA_PROJECT/.tools/kira-deps${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
python3 -m mesonbuild.mesonmain setup .tools/kira-build .tools/kira-source -Dfirefly=false -Dflint=false --prefix="$KIRA_PROJECT/.tools/kira" --wrap-mode=nofallback
ninja -C .tools/kira-build -j 1
ninja -C .tools/kira-build install
.tools/kira/bin/kira --version
sha256sum .tools/kira/bin/kira .tools/downloads/Ferl7.tar.gz
