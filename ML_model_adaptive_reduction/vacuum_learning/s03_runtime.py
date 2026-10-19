"""Exact vacuum integration followed by existing exact rules and a new cost model."""
from s00_vac_common import *
from s01_vacuum import reduce
from s01_propagator import reduce as propagator
from s01_gamma_cancellation import reduce as gamma_tree

def run(c,method='integrated'):
 start=time.perf_counter()
 if method=='previous':return load('vac_prior_runtime',PRIOR/'s02_runtime.py').run(c)
 r=None
 for rule in [reduce,propagator,gamma_tree]:
  r=rule(c)
  if r is not None:break
 if r is not None:return dict(success=True,status='completed',application='vacuum_learning',blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=r)],model_used=False,total_seconds=time.perf_counter()-start)
 parts=batch.support.split_blocks(c)
 if len(parts)>1:
  records=[]
  for part in parts:
   result=run(part['case'],method)
   if not result.get('success'):return dict(success=False,status='incomplete_block_reduction',blocks=records,failed_component=result,total_seconds=time.perf_counter()-start)
   assert len(result['blocks'])==1
   records.append(dict(case=part['case'],indices=part['indices'],result=result['blocks'][0]['result']))
  return dict(success=True,status='completed',application='vacuum_learning',blocks=records,component_count=len(records),model_used=any(b['result'].get('model_used',False) for b in records),total_seconds=time.perf_counter()-start,representation='Product of exact component reductions.')
 sys.path.insert(0,str(HERE));native=load('vac_native_runtime',HERE/'s02_native.py')
 r=native.run(c,'learned' if method=='integrated' else method)
 r['total_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r)
