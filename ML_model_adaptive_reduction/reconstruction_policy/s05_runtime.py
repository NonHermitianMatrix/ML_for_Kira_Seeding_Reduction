"""Preserve the exact dispatch and select the remaining native algebra."""
from s00_reconstruction_common import *
from s04_native import make_runner,BACKENDS

def run(c,method='previous',bunch=1):
 start=time.perf_counter()
 if method=='previous':return previous().run(c,'integrated')
 assert method in BACKENDS
 h=helper();old=h.rt.native.run;h.rt.native.run=make_runner(method,bunch)
 try:
  r=previous().run(c,'integrated')
 finally:h.rt.native.run=old
 r.update(algebra_backend=method,bunch_size=bunch,total_seconds=time.perf_counter()-start)
 return r

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',required=True);p.add_argument('--bunch',type=int,default=1);a=p.parse_args()
 try:r=run(read(a.case),a.method,a.bunch)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-2500:])
 write(a.output,r)
