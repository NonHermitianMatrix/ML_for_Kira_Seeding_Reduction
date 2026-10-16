"""Isolate the published workflow imports and use the current exact Kira build."""
import contextlib, importlib.util, json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'Kira_comparison/higher_scattering'))
import s03_ablation as previous

spec = importlib.util.spec_from_file_location('adaptive_native', HERE / 's01_native_runner.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
run_native = native.run
worker_limit = 2

def adapted(*args, **kwargs):
    os.environ.update(KIRA_RUNTIME_BINARY=str(ROOT / '.tools/kira-adaptive/kira'),
        KIRA_RUNTIME_SCRATCH='node', KIRA_EPHEMERAL_DB='1',
        KIRA_RESTRICT_SECTOR_INIT='1', KIRA_PROJECT_ZERO_CRITERION='1',
        KIRA_INDEX_SECTOR_FILES='1')
    kwargs.update(timeout=180, scratch_cap=32*1024**2, archive=False, records=False)
    kwargs['threads'] = min(kwargs.get('threads', 1), worker_limit)
    return run_native(*args, **kwargs)

# The old thread context temporarily replaces the first three owners. Its own
# native entry point must therefore also use this adapter.
for owner in [previous.runtime.native, previous.bw.native, previous.st, previous.gm.tr]:
    owner.run = adapted

print(json.dumps({'ready': True}), flush=True)
for line in sys.stdin:
    request = json.loads(line)
    if request.get('stop'):
        break
    worker_limit = request.get('workers', 2)
    assert worker_limit in (1, 2)
    try:
        with contextlib.redirect_stdout(sys.stderr):
            r = previous.run(request['case'], request['basis'], 'worker_model', None)
        print(json.dumps({'result': r}, separators=(',', ':')), flush=True)
    except Exception as error:
        print(json.dumps({'error': type(error).__name__ + ': ' + str(error)}), flush=True)
