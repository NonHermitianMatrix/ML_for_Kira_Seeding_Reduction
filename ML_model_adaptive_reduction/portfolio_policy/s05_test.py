"""Compare a frozen model and three complete-time controls on reserved inputs."""
from s02_collect import *
def main(w):
 f=read(HERE/'trained_model/freeze.json');assert f['complete']
 assert f['production_sha256']==inputs.sha(HERE/'s08_reduce.py')
 assert f['application_sha256']==inputs.sha(HERE/'s01_application.py')
 for n,h in f['model_sha256'].items():assert inputs.sha(HERE/'trained_model'/n)==h
 d=read(HERE/'protocol.json')
 for c in d['splits']['reserved'][w::2]:
  p=HERE/'coverage'/(c['id']+'.json')
  if p.exists():continue
  ref=reference(c)
  if ref is None:write(p,dict(case=c['id'],status='reference_unavailable'));continue
  basis=read(ref)['masters'];failed=set();methods=['native','fixed','learned','previous','production']
  for rep in range(d['repetitions']):
   j=(sum(c['id'].encode())+rep)%len(methods)
   for m in methods[j:]+methods[:j]:
    r=call(c,m,HERE/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz'),basis,ref)
    if not r['success']:failed.add(m)
  write(p,dict(case=c['id'],status='verified' if not failed else 'method_failed',failed_methods=sorted(failed),masters=len(basis),nontrivial=any(row and row!={t:'1'} for t,row in read(ref)['coefficients'].items())))
 write(HERE/('test_'+str(w)+'_complete.json'),dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
