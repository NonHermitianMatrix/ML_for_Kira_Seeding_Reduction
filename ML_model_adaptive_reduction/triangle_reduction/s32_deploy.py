"""Production reduction with exact formulas and robust scratch monitoring."""
from s00_triangle_common import *
from s03_triangle_runtime import run as core
from s30_monitor import monitor

def run(c,action='integrated'):
 with monitor(c) as scanner:r=core(c,action)
 r['native_storage_scan']=scanner.record();return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--action',default='integrated');a=p.parse_args()
 try:r=run(read(a.case),a.action)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1600:])
 write(a.output,r)
