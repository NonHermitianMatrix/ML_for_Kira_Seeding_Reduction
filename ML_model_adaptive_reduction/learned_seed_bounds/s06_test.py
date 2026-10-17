"""Run the frozen learned choice and all-ML-disabled controls on reserved inputs."""
import json,time
from s00_inputs import *
from s02_development import reference
import s01_runtime as rt

def main():
 protocol=rt.read(HERE/'protocol.json');fit=rt.read(HERE/'trained_model/selection.json');assert fit['complete']
 assert fit['model_sha256']==sha(HERE/'trained_model/freeze.json')
 assert fit['protocol_sha256']==sha(HERE/'protocol.json')
 out=HERE/'model_test';out.mkdir(exist_ok=True)
 for i,c in enumerate(protocol['splits']['reserved']):
  ref=reference(c)
  if ref is None:
   write(out/(c['id']+'_excluded.json'),dict(case=c['id'],reason='Reference or independent check failed within resource limits.'))
   continue
  basis=rt.read(ref)['masters']
  for repeat in range(protocol['repetitions']):
   methods=protocol['methods'];offset=(i+repeat)%len(methods);methods=methods[offset:]+methods[:offset]
   for method in methods:
    p=out/(c['id']+'_'+method+f'_r{repeat}.json.gz')
    if p.exists():continue
    r=rt.run(c,basis,method=method,reference=ref);r.update(repeat=repeat,model_sha256=fit['model_sha256'] if method=='learned' else None)
    if method!='learned':assert r['model_loading_seconds']==0 and r['decision_seconds']==0 and r['scores'] is None
    assert r['no_other_ml'] and all(a['learned_algebra_disabled'] for a in r['attempts'])
    rt.save(p,r);print(json.dumps(dict(case=c['id'],method=method,repeat=repeat,success=r['success'],seconds=r['complete_seconds'],action=r['first_action'],fallbacks=r['fallbacks'])),flush=True)
 write(out/'completion.json',dict(complete=True,model_sha256=fit['model_sha256'],protocol_sha256=sha(HERE/'protocol.json')))
if __name__=='__main__':main()
