"""Use analytic recurrences first, then the frozen learned/native application."""
from s01_common import *

def run(c,method='learned'):
 assert method in ['learned','fixed','native']
 saved_exact=previous.exact;saved_basis=previous.basis_for
 try:
  previous.exact=exact if method!='native' else h.exact
  previous.basis_for=lambda c,cache:basis(c)
  r=previous.run(c,{'learned':'learned','fixed':'fixed','native':'raw_native'}[method])
  r['application']='analytic_decomposition';return r
 finally:previous.exact=saved_exact;previous.basis_for=saved_basis

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned');a=p.parse_args()
 try:r=run(READ(a.case),a.method)
 except Exception as error:r=dict(success=False,status='exception',error=repr(error),traceback=traceback.format_exc()[-1500:])
 write(a.output,r);print(json.dumps(dict(success=r['success'],status=r['status'])))
