"""Apply exact formulas, validated algebra selection, and bounded recovery."""
from s00_reconstruction_common import *
from s05_runtime import run as backend_run
from s13_cost_decision import choose,features

@lru_cache(None)
def reconstruction_processor():
 try:
  return any(line.startswith('model name') and 'Intel' in line and 'Gold' in line for line in Path('/proc/cpuinfo').read_text().splitlines())
 except OSError:return False

def formula_vacuum(c):
 if c['definition']['external_momenta']:return False
 previous()
 vacuum=load('reconstruction_vacuum_admission',PREVIOUS/'s05_vacuum.py')
 if vacuum.factors(c) is not None or vacuum.scaleless(c) is not None:return True
 path=ROOT/'ML_model_adaptive_reduction/vacuum_learning'
 sys.path.insert(0,str(path))
 tree=load('reconstruction_tree_admission',path/'s01_vacuum.py')
 return tree.recognize(c) is not None

def run(c,method='integrated'):
 start=time.perf_counter()
 if method=='before_formulas':return previous().current().run(c,'integrated')
 if method=='previous':return previous().run(c,'integrated')
 # The new native training grid contains two- and three-loop problems.
 # Other loop orders retain their existing exact and native dispatch directly.
 if len(c['definition']['loop_momenta']) not in (2,3):
  return previous().run(c,'integrated')
 # Formula-only vacuum reductions do not need the reconstruction model.
 if formula_vacuum(c):
  return previous().run(c,'integrated')
 if not reconstruction_processor():
  r=previous().run(c,'integrated');r['reconstruction_admission']='processor_outside_verified_build_environment';return r
 tick=time.perf_counter();deployment=read(HERE/'trained_model/deployment.json')
 policy=read(HERE/'trained_model'/('fixed.json' if method=='fixed' else deployment['configuration']));load_seconds=time.perf_counter()-tick
 tick=time.perf_counter();action,info=choose(policy,features(c),method!='fixed',helper().inputs.signature(c));decision=time.perf_counter()-tick
 backend,bunch=policy['settings'][action]
 r=backend_run(c,backend,bunch);first_success=r.get('success',False)
 if not first_success and action!='previous':
  failed=r;r=previous().run(c,'integrated')
  r['reconstruction_failed_attempt']=failed
 r.update(reconstruction_action=action,reconstruction_decision=info,reconstruction_model_loading_seconds=load_seconds,reconstruction_decision_seconds=decision,reconstruction_fallback=not first_success and action!='previous',total_seconds=time.perf_counter()-start)
 return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-2000:])
 write(a.output,r)
