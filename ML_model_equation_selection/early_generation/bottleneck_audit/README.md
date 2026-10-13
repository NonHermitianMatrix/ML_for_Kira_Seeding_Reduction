# bottleneck audit

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

[s00_timestamp.py](s00_timestamp.py)

This module supports the local calculation.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

Path(os.environ['KIRA_PROFILE_EVENTS']).write_text(json.dumps(events))

```

[s01_profile.py](s01_profile.py)

This module supports the local calculation.

The imported project modules are `s03_profile_run`, `s04_experiment`.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(out / 'completed.json').write_text(json.dumps({'count': len(selected) * 3, 'success': True, 'scope': 'diagnostic timestamps; native equations and exact reference checks; no model changes'}))

```

[s02_profile.sh](s02_profile.sh)

This shell script runs the recorded commands for this stage.

This is a scheduler job script. Submit it with `qsub` from the project root.

The exact command sequence is:

```bash

#!/bin/bash
#$ -cwd
#$ -q pod_smp.q
#$ -S /bin/bash
#$ -N KiraBottleneck
#$ -l h_rt=00:10:00,h_data=3G,h_vmem=6G
#$ -j y
set -euo pipefail
source /u/local/Modules/default/init/modules.sh
module load python/3.9.6
export LC_ALL=C LANG=C PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2867200
ulimit -c 0
.tools/seed-model/venv/bin/python .tools/bottleneck-audit/s01_profile.py

```

[s03_profile_run.py](s03_profile_run.py)

The program runs one bounded complete Kira reduction, retaining compact exact evidence.

The module defines these callable interfaces:

```python

def sha(p)
def label(a)
def limits()
def disk(path)
def process_rss(pid)
def parse_export(text)
def run(case, size, policy, output, timeout=300, margin=1, reference=None, weights=None, records=True, archive=True, check_masters=False, force=None, scratch_cap=None, compact=True, ordering=None, basis=None)
def main()

```

The imported external packages are `sympy`.

The imported project modules are `s02_records`, `s07_seed`.

These source constants locate inputs and outputs:

```python

MODEL_HOME = pathlib.Path('/u/home/r/rushil/ML_for_Kira_Seeding_Reduction/ML_model_equation_selection')
HERE = ROOT / 'Kira_comparison/integrated_runtime'
MODEL = ROOT / 'ML_model_reduction/cost_training'

```

The command accepts these parser options:

- `'case'`: The parser accepts a value..
- `'--size'`: type=int; default=8.
- `'--policy'`: default='stock'.
- `'--timeout'`: type=int; default=300.
- `'--margin'`: type=int; default=1.
- `'--output'`: type=pathlib.Path; required=True.
- `'--reference'`: type=pathlib.Path.
- `'--weights'`: type=pathlib.Path.
- `'--no-records'`: action='store_true'.
- `'--legacy-backsub'`: action='store_true'.
- `'--check-masters'`: action='store_true'.
- `'--ordering'`: type=int.

These calls show the stored input and output interface:

```python

(HERE / 'resource_plan.json').read_text()
(scratch / 'config/integralfamilies.yaml').write_text(json.dumps(config))
(scratch / 'config/kinematics.yaml').write_text(json.dumps(dict(kinematics=kin)))
(scratch / 'targets').write_text(''.join((label(a) + '\n' for a in target)))
(scratch / 'jobs.yaml').write_text(json.dumps(jobs))
(scratch / 'equation_context.txt').write_text(f"{len(definition['loop_momenta'])} {len(ext)} {len(target)} {n}\n" + '\n'.join((' '.join(map(str, a)) for a in target)) + '\n')
(scratch / 'run.log').read_text(errors='replace')
(scratch / 'masters').write_text(''.join((label(a) + '\n' for a in basis)))
(scratch / 'seeds.txt').write_text(''.join((label(a) + '\n' for a in selected)))
(scratch / '.kira_ephemeral_trial').write_text('Disposable fresh calculation; discard after interruption.\n')
(scratch / 'equations.tsv').read_text()
(scratch / 'choices.jsonl').read_text()
paths[0].read_text()
(HERE / 'families.json').read_text()
p.read_bytes()
(scratch / 'equation_metrics.json').read_text()
(scratch / 'seed_audit.json').read_text()
(base / 'status').read_text()
(scratch / 'stage_metrics.jsonl').read_text()
(scratch / 'metrics.jsonl').read_text()
(thread / 'children').read_text()

```

[s04_summarize.py](s04_summarize.py)

The program summarizes non-overlapping diagnostic log intervals and existing native timers.

Import this helper module from the stage that uses it.

These calls show the stored input and output interface:

```python

(p / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
f.read_text()
(p / 'completed.json').read_text()
x.read_bytes()

```

## Data and supporting files

- [completed.json](completed.json): This file contains structured records from the parent calculation.

- [equation_test_00_sunrise_n21_r0.json.gz](equation_test_00_sunrise_n21_r0.json.gz): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r0_events.json](equation_test_00_sunrise_n21_r0_events.json): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r1.json.gz](equation_test_00_sunrise_n21_r1.json.gz): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r1_events.json](equation_test_00_sunrise_n21_r1_events.json): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r2.json.gz](equation_test_00_sunrise_n21_r2.json.gz): This file records the source equations or their checks.

- [equation_test_00_sunrise_n21_r2_events.json](equation_test_00_sunrise_n21_r2_events.json): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r0.json.gz](equation_test_02_double_box_n128_r0.json.gz): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r0_events.json](equation_test_02_double_box_n128_r0_events.json): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r1.json.gz](equation_test_02_double_box_n128_r1.json.gz): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r1_events.json](equation_test_02_double_box_n128_r1_events.json): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r2.json.gz](equation_test_02_double_box_n128_r2.json.gz): This file records the source equations or their checks.

- [equation_test_02_double_box_n128_r2_events.json](equation_test_02_double_box_n128_r2_events.json): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r0.json.gz](equation_test_06_ladder3_n128_r0.json.gz): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r0_events.json](equation_test_06_ladder3_n128_r0_events.json): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r1.json.gz](equation_test_06_ladder3_n128_r1.json.gz): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r1_events.json](equation_test_06_ladder3_n128_r1_events.json): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r2.json.gz](equation_test_06_ladder3_n128_r2.json.gz): This file records the source equations or their checks.

- [equation_test_06_ladder3_n128_r2_events.json](equation_test_06_ladder3_n128_r2_events.json): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r0.json.gz](equation_test_07_ladder3_n128_r0.json.gz): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r0_events.json](equation_test_07_ladder3_n128_r0_events.json): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r1.json.gz](equation_test_07_ladder3_n128_r1.json.gz): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r1_events.json](equation_test_07_ladder3_n128_r1_events.json): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r2.json.gz](equation_test_07_ladder3_n128_r2.json.gz): This file records the source equations or their checks.

- [equation_test_07_ladder3_n128_r2_events.json](equation_test_07_ladder3_n128_r2_events.json): This file records the source equations or their checks.

- [initial_wrapper_guard_failure.json.gz](initial_wrapper_guard_failure.json.gz): This file contains structured records from the parent calculation.

- [initial_wrapper_guard_failure.log](initial_wrapper_guard_failure.log): This file contains saved program messages.

- [job.log](job.log): This file contains saved program messages.

- [summary.json](summary.json): This file contains the result counts and summary measurements.
