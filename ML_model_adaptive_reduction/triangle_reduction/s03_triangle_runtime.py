"""Direct triangle formulas, then a frozen or explicitly chosen native backend."""
from s00_triangle_common import *
from s01_triangle import reduce

def run(c,action='integrated'):
 start=time.perf_counter()
 if action=='previous':return prior().run(c,'integrated')
 if action=='symbolic_prior':return prior().previous().run(c,'integrated')
 r=reduce(c)
 if r is not None:return r
 if action in ['integrated','fixed']:
  # Updated only after validation. The preceding application remains the default.
  model=HERE/'trained_model/policy.json'
  if not model.exists():return prior().run(c,'integrated')
  from s08_triangle_train import choose
  m=read(model);action=choose(c,m,action=='integrated')
  r=run(c,action);r.update(native_policy_action=action,native_cost_model_enabled=bool(m['enabled']),total_seconds=time.perf_counter()-start);return r
 if action=='baseline':return prior().run(c,'integrated')
 assert action in ['ff1','ff4','ff8','ff16','symbolic']
 backend='symbolic' if action=='symbolic' else 'firefly';bunch=1 if action=='symbolic' else int(action[2:])
 r=prior().backend_run(c,backend,bunch)
 if not r.get('success'):
  failed=r;r=prior().run(c,'integrated');r['new_failed_attempt']=failed
 r.update(native_action=action,total_seconds=time.perf_counter()-start);return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--action',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.action)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1500:])
 write(a.output,r)
