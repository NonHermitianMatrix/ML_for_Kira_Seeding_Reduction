"""Apply proved connected-subintegral identities before the existing learned policy."""
from s00_loop_common import *
from s01_bubble_tree import reduce

def run(c,method='integrated'):
 begin=time.perf_counter()
 r=reduce(c) if method=='integrated' else None
 if r is not None:
  return dict(success=True,status='completed',application='connected_bubble_tree',blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=r)],model_used=False,total_seconds=time.perf_counter()-begin)
 result=prior().run(c,'all_fixed' if method=='all_fixed' else 'learned')
 result.update(coverage13_method=method,total_seconds=time.perf_counter()-begin);return result
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
 write(a.output,r)
