"""Test the frozen equation classifier inside the validated reconstruction call."""
from s00_triangle_common import *
from s03_triangle_runtime import run as core_run
WEIGHTS=ROOT/'ML_model_equation_selection/scattering_training/trained_model/nonplanar_box.txt'

def filtered_run(c,mode='off'):
 if mode=='off' or c.get('topology_group')!='nonplanar_box':return core_run(c,'integrated')
 assert mode=='on'
 model=read(HERE/'trained_model/policy.json')
 if helper().inputs.signature(c) not in model['signatures'].get('nonplanar_box',[]):return core_run(c,'integrated')
 old=prior();namespace=old.backend_run.__globals__;factory=namespace['make_runner'];state=dict(attempts=0,disabled_after_failure=False,metrics=[])
 def make(backend,bunch):
  native=factory(backend,bunch)
  def wrapped(*args,**kwargs):
   active=not state['disabled_after_failure'];keys=['KIRA_EQ_MODE','KIRA_EQ_WEIGHTS','KIRA_EQ_THRESHOLD'];saved={k:os.environ.get(k) for k in keys}
   if active:os.environ.update(KIRA_EQ_MODE='learned',KIRA_EQ_WEIGHTS=str(WEIGHTS),KIRA_EQ_THRESHOLD='.05')
   try:
    result=native(*args,**kwargs)
    if active:
     state['attempts']+=1;state['metrics'].append(result.get('equation_metrics',{}));result['added_equation_filter']=True
     if not result.get('success'):state['disabled_after_failure']=True
    return result
   finally:
    for k,v in saved.items():
     if v is None:os.environ.pop(k,None)
     else:os.environ[k]=v
  return wrapped
 namespace['make_runner']=make
 try:r=core_run(c,'integrated')
 finally:namespace['make_runner']=factory
 r['equation_filter_extension']=dict(state,weights_sha256=sha(WEIGHTS),threshold=.05);return r

def run(c,mode='off'):
 from s30_monitor import monitor
 with monitor(c) as scan:r=filtered_run(c,mode)
 r['native_storage_scan']=scan.record();return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--mode',required=True);a=p.parse_args()
 try:r=run(read(a.case),a.mode)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1600:])
 write(a.output,r)
