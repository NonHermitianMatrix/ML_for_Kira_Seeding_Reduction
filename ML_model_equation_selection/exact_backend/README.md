# exact backend

This folder supports the calculation described in the parent guide.

Read [the parent guide](../README.md) for the stage and data flow.

## Code use

Run scientific calculations on Hoffman in a scheduled job.
Load the Python 3.9.6 module and use the existing project environment.
The usual interpreter is `.tools/seed-model/venv/bin/python` from the project root.
Build scripts state their compiler and native Kira requirements.
Keep each script's memory, time and storage limits.
Keep existing model and test files before a new run.
Scripts that write reports describe earlier document names; review their destinations before use.

## Code files

The entries below follow file-name order.
Each entry gives its purpose and the input or output interface available in the source.

[s00_backend.py](s00_backend.py)

The file provides exact integer polynomials, bounded binary records and legacy compatibility.

The module defines these callable interfaces:

```python

def read(p)
def write(p, x)
def sha(p)
def allocated(p)
def guard()
def big(x)
def u(x)
class Reader
def common_packet(rows, loops)
def read_common(data)
def native(data, state)
def python_expand(rows, loops, state)
def row_keys(rows)
def regroup(polys, keys)
def decode_expanded(data, keys)
def symbolic(rows)
def binary_payload(parts)
def decode_binary(data)
def object_store(raw, suffix, folder=HERE / 'objects')
def save(path, result, folder=None)
def load_coeff(r, folder=HERE / 'objects')
def dependencies(c, policy)
def recurrence(c, rows)
class TaylorInteger
def features(requests)
def predict(requests, state)

```

The imported project modules are `s00_arithmetic`, `s01_engine`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
POLY = HERE.parent / 'polynomial_reuse'

```

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

Path(p).read_text()
p.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
(folder / (r['coefficients_sha256'] + suffix)).read_bytes()

```

[s01_transform.cpp](s01_transform.cpp)

The file provides bounded exact polynomial transformations with GMP.

The required headers are `gmpxx.h`, `vector`, `map`, `string`, `stdexcept`, `cstdint`, `cstdlib`, `cstring`.

The matching build script compiles this file with its caller.

The public compiled interface is:

```cpp

extern "C" int expand_exact(const void*data,size_t n,void**output,size_t*outn){
extern "C" void release_exact(void*p){std::free(p);}

```

Use the parent stage guide for the build order and input records.

[s02_engine.py](s02_engine.py)

The file provides shared integer representation with compiled expansion and learned batch routing.

The module defines these callable interfaces:

```python

def calculate(requests, mode, state, forced_policy=None, inject_failure=False)
def apply(requests, mode, state=None, forced_policy=None, inject_failure=False)

```

The imported project modules are `s00_backend`.

Import this helper module from the stage that uses it.

[s03_application.py](s03_application.py)

The file provides bounded single-batch and persistent interfaces with lossless coefficient output.

The module defines these callable interfaces:

```python

def process(cmd, mode, state, forced_policy=None)
def main()

```

The imported project modules are `s02_engine`.

The command accepts these parser options:

- `'--input'`: The parser accepts a value..
- `'--output'`: The parser accepts a value..
- `'--mode'`: default='deployed'; choices=MODES + ['deployed'].
- `'--policy'`: choices=POLICIES.
- `'--stream'`: action='store_true'.
- `'--max-requests'`: type=int; default=64.

[s04_check.py](s04_check.py)

The program checks exact arithmetic, binary round trips, worker isolation and Kira fallback.

The module defines these callable interfaces:

```python

def kernel()
def integration()

```

The imported project modules are `s02_engine`.

The command accepts these parser options:

- `'stage'`: choices=['kernel', 'integration'].

These calls show the stored input and output interface:

```python

(HERE / 'objects' / (r['coefficients_sha256'] + '.bin.gz')).read_bytes()

```

[s05_study.py](s05_study.py)

The program collects complete runtime labels, validate policies, then freeze independent tests.

The module defines these callable interfaces:

```python

def prepare()
def labels()
def train()
def arms(stage)
def key(mode, policy)
def trials(stage)
def ratios(rows, metric)
def freeze()
def check_freeze()
def streams()
def main()

```

The imported external packages are `numpy`, `sklearn`.

The imported project modules are `s02_engine`.

The command accepts these parser options:

- `'stage'`: choices=['prepare', 'labels', 'train', 'validation', 'freeze', 'test', 'streams'].

[s06_run.sh](s06_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExactStudy
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=ML_model_equation_selection/exact_backend
if [ "$1" = build ]; then
 mkdir -p "$P/build" "$P/development"
 g++ -O3 -std=c++11 -fPIC -shared "$P/s01_transform.cpp" -lgmpxx -lgmp -o "$P/build/transform.so"
 .tools/seed-model/venv/bin/python - <<'PY'
import ctypes,json,hashlib,subprocess
from pathlib import Path
p=Path('ML_model_equation_selection/exact_backend')
lib=ctypes.CDLL('libgmp.so.10')
d=dict(compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
 gmp_version=ctypes.c_char_p.in_dll(lib,'__gmp_version').value.decode(),
 source_sha256=hashlib.sha256((p/'s01_transform.cpp').read_bytes()).hexdigest(),
 library_sha256=hashlib.sha256((p/'build/transform.so').read_bytes()).hexdigest(),
 command='g++ -O3 -std=c++11 -fPIC -shared s01_transform.cpp -lgmpxx -lgmp -o build/transform.so')
(p/'build/build.json').write_text(json.dumps(d,indent=2)+'\n')
print(d,flush=True)
PY
 .tools/seed-model/venv/bin/python "$P/s04_check.py" kernel
else
 test ! -e "$P/freeze.json"
 .tools/seed-model/venv/bin/python "$P/s05_study.py" prepare
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" labels
 .tools/seed-model/venv/bin/python "$P/s05_study.py" train
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" validation
 .tools/seed-model/venv/bin/python "$P/s05_study.py" freeze
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" test
 .tools/seed-model/venv/bin/python -u "$P/s05_study.py" streams
 .tools/seed-model/venv/bin/python "$P/s04_check.py" integration
fi

```

[s07_audit.py](s07_audit.py)

The program audits reserved coefficients, binary readers and fixed policies.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s05_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'objects' / (eh + '.json.gz')).read_bytes()

```

[s08_analyze.py](s08_analyze.py)

The program summarizes frozen complete timings, decoding costs and model comparisons.

The module defines these callable interfaces:

```python

def compare(rows, left, right, metric)
def main()

```

The imported project modules are `s05_study`.

This entry point uses the paths and options set in its source.

[s09_plot.py](s09_plot.py)

The program plots exact arithmetic, complete output costs and learned strategy results.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s00_backend`.

This entry point uses the paths and options set in its source.

[s10_document.py](s10_document.py)

The program documents both frozen comparisons, the new cost model and final deployment.

The module defines these callable interfaces:

```python

def block(path, key, text)
def main()

```

The imported project modules are `s00_backend`.

The command accepts these parser options:

- `'--data-commit'`: The parser accepts a value..

These calls show the stored input and output interface:

```python

path.read_text()
path.write_text(old)
(HERE / 'report_template.tex.in').read_text()
(ROOT / 'report/exact_backend.tex').write_text(t)
p.read_text()
p.write_text(old)
p.write_text(old + '\n' + '\\input{exact_backend}' + '\n')
p.write_text(old.replace('polynomial_reuse.tex references.bib', 'polynomial_reuse.tex exact_backend.tex references.bib'))
(HERE / folder / 'README.md').write_text(description + '\n')
(folder / 'README.md').write_text(desc + '\n')
f.read_text()

```

[s11_release_check.py](s11_release_check.py)

The program verifies both frozen studies, exact evidence, report references and storage bounds.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s16_reader_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(ROOT / 'report/report.tex').read_text()
(ROOT / 'report/exact_backend.tex').read_text()
p.read_text()
(ROOT / 'report/references.bib').read_text()
p.read_bytes()

```

[s12_report.sh](s12_report.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExactReport
#$ -l h_rt=00:20:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python ML_model_equation_selection/exact_backend/s10_document.py "$@"
.tools/seed-model/venv/bin/python ML_model_equation_selection/exact_backend/s11_release_check.py
make -C report all

```

[s13_reader.cpp](s13_reader.cpp)

The file provides lossless coefficient reader for the existing expanded binary format.

The required headers are `Python.h`, `cstdint`, `stdexcept`, `memory`.

The matching build script compiles this file with its caller.

Use the parent stage guide for the build order and input records.

[s14_reader.py](s14_reader.py)

The program uses a compiled lossless reader without changing the first frozen implementation.

The module defines these callable interfaces:

```python

def compiled_reader(data, keys)
def main()

```

The imported project modules are `s00_backend`, `s02_engine`, `s04_check`.

These source constants locate inputs and outputs:

```python

HERE = Path(__file__).resolve().parent

```

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

kernel_path.read_bytes()

```

[s15_application.py](s15_application.py)

The file provides public interface for the validated arithmetic and compiled-reader extension.

The module defines these callable interfaces:

```python

def main()

```

The imported project modules are `s00_backend`, `s02_engine`, `s03_application`, `s14_reader`.

The command accepts these parser options:

- `'--input'`: The parser accepts a value..
- `'--output'`: The parser accepts a value..
- `'--mode'`: choices=MODES + ['deployed']; default='deployed'.
- `'--policy'`: choices=POLICIES.
- `'--stream'`: action='store_true'.
- `'--max-requests'`: type=int; default=64.

[s16_reader_study.py](s16_reader_study.py)

The file provides fresh validation and reserved tests for the compiled coefficient reader.

The module defines these callable interfaces:

```python

def prepare()
def arms(stage)
def trials(stage)
def freeze()
def streams()
def check_freeze()
def main()

```

The imported project modules are `s02_engine`, `s05_study`, `s14_reader`.

The command accepts these parser options:

- `'stage'`: choices=['prepare', 'validation', 'freeze', 'test', 'streams'].

[s17_reader_run.sh](s17_reader_run.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExactReader
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=ML_model_equation_selection/exact_backend
test ! -e "$P/reader_freeze.json"
.tools/seed-model/venv/bin/python - <<'PY'
from pathlib import Path
import sys,sysconfig,subprocess,json,hashlib
p=Path('ML_model_equation_selection/exact_backend')
cmd=['g++','-O3','-std=c++11','-fPIC','-shared','-I'+sysconfig.get_path('include'),str(p/'s13_reader.cpp'),'-o',str(p/'build/reader.so')]
subprocess.run(cmd,check=True,timeout=90)
d=dict(command=cmd,python_version=sys.version,source_sha256=hashlib.sha256((p/'s13_reader.cpp').read_bytes()).hexdigest(),library_sha256=hashlib.sha256((p/'build/reader.so').read_bytes()).hexdigest())
(p/'build/reader_build.json').write_text(json.dumps(d,indent=2)+'\n')
PY
.tools/seed-model/venv/bin/python "$P/s14_reader.py"
.tools/seed-model/venv/bin/python "$P/s16_reader_study.py" prepare
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" validation
.tools/seed-model/venv/bin/python "$P/s16_reader_study.py" freeze
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" test
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" streams
.tools/seed-model/venv/bin/python "$P/s18_reader_audit.py"
.tools/seed-model/venv/bin/python "$P/s19_reader_analyze.py"
.tools/seed-model/venv/bin/python "$P/s20_reader_plot.py"

```

[s18_reader_audit.py](s18_reader_audit.py)

The program audits reserved coefficients, binary readers and fixed policies.

The module defines these callable interfaces:

```python

def audit()
def integration()
def reader_comparison()

```

The imported project modules are `s14_reader`, `s16_reader_study`.

This entry point uses the paths and options set in its source.

These calls show the stored input and output interface:

```python

(HERE / 'objects' / (r['coefficients_sha256'] + '.bin.gz')).read_bytes()
(HERE / 'objects' / (eh + '.json.gz')).read_bytes()
(HERE / 'objects' / (record['coefficients_sha256'] + '.bin.gz')).read_bytes()

```

[s19_reader_analyze.py](s19_reader_analyze.py)

The program summarizes frozen complete timings, decoding costs and model comparisons.

The module defines these callable interfaces:

```python

def compare(rows, left, right, metric)
def main()

```

The imported project modules are `s16_reader_study`.

This entry point uses the paths and options set in its source.

[s20_reader_plot.py](s20_reader_plot.py)

The program plots exact arithmetic, complete output costs and learned strategy results.

The module defines these callable interfaces:

```python

def main()

```

The imported external packages are `matplotlib`.

The imported project modules are `s14_reader`.

This entry point uses the paths and options set in its source.

[s21_reader_finish.sh](s21_reader_finish.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraExactFinal
#$ -l h_rt=01:00:00,h_data=3G,h_vmem=4G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
P=ML_model_equation_selection/exact_backend
test ! -e "$P/reader_final_freeze.json"
.tools/seed-model/venv/bin/python "$P/s16_reader_study.py" prepare
.tools/seed-model/venv/bin/python "$P/s16_reader_study.py" freeze
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" test
.tools/seed-model/venv/bin/python -u "$P/s16_reader_study.py" streams
.tools/seed-model/venv/bin/python "$P/s18_reader_audit.py"
.tools/seed-model/venv/bin/python "$P/s19_reader_analyze.py"
.tools/seed-model/venv/bin/python "$P/s20_reader_plot.py"

```

## Data and supporting files

- [audit_scheduler.log](audit_scheduler.log): This file records checks of the corresponding calculation.

- [build_scheduler.log](build_scheduler.log): This file contains saved program messages.

- [deployment.json](deployment.json): This file contains structured records from the parent calculation.

- [final_report_scheduler.log](final_report_scheduler.log): This file contains saved program messages.

- [freeze.json](freeze.json): This file identifies the fixed inputs and method for the completed test.

- [protocol.json](protocol.json): This file contains structured records from the parent calculation.

- [reader_deployment.json](reader_deployment.json): This file contains structured records from the parent calculation.

- [reader_final_deployment.json](reader_final_deployment.json): This file contains structured records from the parent calculation.

- [reader_final_freeze.json](reader_final_freeze.json): This file contains structured records from the parent calculation.

- [reader_final_protocol.json](reader_final_protocol.json): This file contains structured records from the parent calculation.

- [reader_final_scheduler.log](reader_final_scheduler.log): This file contains saved program messages.

- [reader_freeze.json](reader_freeze.json): This file contains structured records from the parent calculation.

- [reader_protocol.json](reader_protocol.json): This file contains structured records from the parent calculation.

- [reader_scheduler.log](reader_scheduler.log): This file contains saved program messages.

- [report_scheduler.log](report_scheduler.log): This file contains saved program messages.

- [report_template.tex.in](report_template.tex.in): This file supports the calculation described in the parent guide.

- [resource_plan.json](resource_plan.json): This file sets storage, memory and execution limits.

- [study_scheduler.log](study_scheduler.log): This file contains saved program messages.

## Child folders

- [build](build/README.md).

- [development](development/README.md).

- [model_test](model_test/README.md).

- [objects](objects/README.md).

- [reader_final_test](reader_final_test/README.md).

- [reader_test](reader_test/README.md).

- [reader_validation](reader_validation/README.md).

- [trained_model](trained_model/README.md).

- [training](training/README.md).

- [validation](validation/README.md).
