"""Apply exact tensor identities before the preceding exact and native ML rules."""
from s00_tensor_common import *
from s01_tensor import eligible,reduce

def run(c,method='integrated'):
 start=time.perf_counter();used=False
 if method!='previous' and eligible(c):
  tick=time.perf_counter();action,used=choice(c,method);prediction=time.perf_counter()-tick
  r=reduce(c,action,deadline=time.perf_counter()+12)
  if r is not None:
   r.update(model_used=used,prediction_seconds=prediction)
   return dict(success=True,status='completed',application='tensor_reduction',blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=r)],model_used=used,total_seconds=time.perf_counter()-start)
 old=previous()
 if method!='previous' and len(c['definition']['loop_momenta'])>1:
  parts=old.batch.support.split_blocks(c)
  if len(parts)>1:
   records=[];memo={}
   for part in parts:
    cc=part['case'];key=json.dumps([cc['definition'],cc['targets']],sort_keys=True)
    if key not in memo:memo[key]=run(cc,method)
    result=memo[key]
    if not result.get('success'):return dict(success=False,status='incomplete_block_reduction',blocks=records,failed_component=result,total_seconds=time.perf_counter()-start)
    assert len(result['blocks'])==1
    records.append(dict(indices=part['indices'],case=cc,result=result['blocks'][0]['result']))
   return dict(success=True,status='completed',application='tensor_reduction',blocks=records,model_used=any(b['result'].get('model_used',False) or b['result'].get('batch_model_used',False) for b in records),total_seconds=time.perf_counter()-start,representation='Product of exact independent component reductions.')
 # Keep the preceding deployed ML policy for inputs outside the new identity.
 r=old.run(c,'all_fixed' if method=='all_fixed' else 'integrated');r['total_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r)
