"""Check the corrected import binding before repeating the frozen comparison."""
from s00_direct_common import *
from s25_deploy_measure import measured
from s27_deploy_test import compare

def main():
 p=read(HERE/'import_conflict/final_protocol.json.gz')
 c=next(c for c in p['cases'] if c['test_group']=='native')
 archived=read(HERE/'import_conflict/deployment_test'/(c['id']+'.json.gz'))
 results={}
 for method in ['integrated','fixed','previous']:
  r,t=measured(c,method,2,30);ok,n=compare(c,r,archived['reference'])
  results[method]=dict(success=ok,checks=n,seconds=t,status=r.get('status'))
  assert ok,(method,r)
 write(HERE/'import_check.json',dict(complete=True,case=c['id'],results=results))
 print('Corrected native entry point: all three controls agree with the reference.',flush=True)
if __name__=='__main__':main()
