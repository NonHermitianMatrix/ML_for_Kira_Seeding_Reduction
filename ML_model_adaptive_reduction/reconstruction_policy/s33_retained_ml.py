"""Isolate inherited learned choices with the validated algebra settings fixed."""
from s00_reconstruction_common import *
from s04_native import make_runner
from s13_cost_decision import choose,features
from s15_deploy import reconstruction_processor

def run(c,method):
 assert method in ['retained_ml','retained_fixed']
 assert reconstruction_processor()
 start=time.perf_counter();h=helper()
 policy=read(HERE/'trained_model/fixed.json')
 action,info=choose(policy,features(c),False,h.inputs.signature(c))
 backend,bunch=policy['settings'][action]
 seed_method='integrated' if method=='retained_ml' else 'fixed'
 old=h.rt.native.run
 if backend!='previous':h.rt.native.run=make_runner(backend,bunch)
 try:r=previous().run(c,seed_method)
 finally:h.rt.native.run=old
 if not r.get('success') and action!='previous':
  failed=r;r=previous().run(c,seed_method);r['reconstruction_failed_attempt']=failed
 r.update(retained_ml_control=method,reconstruction_action=action,reconstruction_decision=info,total_seconds=time.perf_counter()-start)
 return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',required=True);a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-2500:])
 write(a.output,r)
