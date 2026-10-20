"""Deploy exact extensions and retain the published native policy unless replaced by validation."""
from s00_direct_common import *
# Older native modules import their own s01_runtime by its short name.
# Give this distinct application a unique module name to preserve that binding.
candidate=load('direct_candidate_runtime',HERE/'s01_runtime.py').run

def run(c,method='integrated'):
 start=time.perf_counter();d=c['definition']
 if method=='previous':return current().run(c,'integrated')
 if method in ['dense','wide'] or method.startswith('order'):return candidate(c,method)
 if len(d['loop_momenta'])==2 and len(d['propagators'])==9 and d['external_momenta']:
  old=current()
  if old.previous().previous().batch.eligible(c):
   new=read(HERE/'trained_model/policy.json')
   if not new['enabled']:
    r=old.run(c,'all_fixed' if method=='fixed' else 'integrated');r.update(native_policy_source='preceding_validated_model',total_seconds=time.perf_counter()-start);return r
 r=candidate(c,method);r['total_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:
  assert Path(a.case).stat().st_size<1024**2;r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r)
