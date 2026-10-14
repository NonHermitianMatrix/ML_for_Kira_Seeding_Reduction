"""Apply one frozen choice before Kira constructs its integral weights."""
import contextlib,importlib.util,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_workflow_selection/basis_completion'))
import s04_train as previous_model
prior=previous_model.w
FROZEN=json.loads((prior.HERE/'trained_model/freeze.json').read_text())
previous_model.check_freeze(FROZEN)
spec=importlib.util.spec_from_file_location('ordering_native',HERE/'s02_native_runner.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

@contextlib.contextmanager
def settings(config):
 threads=int(config.replace('threads',''));assert threads in [2,4]
 def adapted(*args,**kwargs):
  kwargs.update(threads=threads)
  return native.run(*args,**kwargs)
 owners=[prior.native,prior.st,prior.old.tr]
 saved=[o.run for o in owners]
 try:
  for o in owners:o.run=adapted
  yield
 finally:
  for o,f in zip(owners,saved):o.run=f

def previous(c,basis):
 cfg,reason=previous_model.select(FROZEN,c)
 r=prior.workflow(c,basis,cfg)
 r.update(seed_configuration=cfg,seed_selection_reason=reason)
 return r

def workflow(c,basis,config,ref=None):
 start=time.perf_counter()
 if config=='previous':r=previous(c,basis)
 else:
  with settings(config):r=previous(c,basis)
  # Return to the published ordering if the new one does not finish.
  prior.verify(c,r,basis)
  if not r['success']:
   failed=r;r=previous(c,basis)
   r['attempts']=failed['attempts']+r['attempts']
   r['fallback_count']+=1+failed['fallback_count']
 prior.verify(c,r,basis,ref)
 r.update(configuration=config,complete_seconds=time.perf_counter()-start)
 return r
