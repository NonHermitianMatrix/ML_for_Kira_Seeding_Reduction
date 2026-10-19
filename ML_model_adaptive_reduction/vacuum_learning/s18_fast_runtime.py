"""Use the unchanged exact reductions and trained model with bounded output."""
from s00_vac_common import *
from s17_output_budget import output
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='integrated');a=p.parse_args()
 try:
  assert Path(a.case).stat().st_size<3*1024**2
  runtime=load('vac_fast_application',HERE/'s03_runtime.py');r=runtime.run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
 output(a.output,r)
