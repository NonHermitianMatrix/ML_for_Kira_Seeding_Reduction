"""Deploy the recurrence model only after validation of complete application time."""
from s00_fast_common import *
import s03_fast_runtime as candidate

def run(c,method='final'):
 assert method in ['final','candidate','fixed_recurrence']
 enabled=read(HERE/'deployment/admission.json')['enabled'] if method=='final' else method=='candidate'
 original=candidate.choose;original_legacy=candidate.legacy
 if os.environ.get('KIRA_FAST_EXACT_ONLY')=='1':
  def forbid_native():raise RuntimeError('Validation admitted only exact recurrence inputs')
  candidate.legacy=forbid_native
 try:
  if not enabled:candidate.choose=lambda c,m:original(c,'fixed')
  r=candidate.run(c,'learned');r['application']='fast_decomposition_complete_cost';r['recurrence_model_enabled']=enabled;return r
 finally:candidate.choose=original;candidate.legacy=original_legacy

if __name__=='__main__':
 import argparse,traceback
 os.environ['SYMPY_GROUND_TYPES']='python'
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='final');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r);print(json.dumps(dict(success=r['success'],status=r['status'])))
