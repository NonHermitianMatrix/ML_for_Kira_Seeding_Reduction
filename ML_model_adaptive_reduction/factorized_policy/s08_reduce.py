"""Public interface for exact block reductions and learned Kira seed bounds."""
from s00_common import *
from s10_validated_runtime import run as reduce
if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned',choices=['native','fixed','learned']);a=p.parse_args()
 try:r=reduce(READ(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1800:])
 write(a.output,r);print(json.dumps(dict(success=r['success'],status=r['status'])))
