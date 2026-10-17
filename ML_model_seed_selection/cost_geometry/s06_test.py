"""Run frozen same-worker comparisons on reserved physical requests."""
import argparse,hashlib,json,socket,time
from s03_train import reference
from s05_reduce import reduce,feature,predict
from s00_policy import *

def main():
 p=argparse.ArgumentParser();p.add_argument('graph');a=p.parse_args();g=a.graph
 f=HERE/'trained_model'/('cost_'+g+'.json');freeze=rt.read(f)
 protocol=rt.read(HERE/'protocols'/('cost_'+g+'.json'));cases=protocol['reserved'];hashes={str(p.relative_to(HERE)):inputs.sha(p) for p in [f,HERE/'s00_policy.py',HERE/'s05_reduce.py',HERE/'s06_test.py']}
 inputs.write(HERE/'model_test'/(g+'_freeze.json'),dict(hashes=hashes,cases=[c['id'] for c in cases],methods=['native','fixed','learned','previous'],repetitions=7,worker=socket.gethostname(),same_worker_per_case=True))
 for i,c in enumerate(cases):
  refp,ref=reference(c)
  if not ref['success']:continue
  for rep in range(7):
   methods=['native','fixed','learned','previous'];shift=(i+rep)%4;methods=methods[shift:]+methods[:shift]
   for method in methods:
    out=HERE/'model_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
    if out.exists():continue
    r=reduce(c,ref['masters'],method,refp);r.update(repetition=rep,worker=socket.gethostname());save(out,r)
    print(json.dumps(dict(case=c['id'],method=method,repetition=rep,success=r['success'],seconds=r['complete_seconds'],fallbacks=r['fallbacks'],choice=r.get('selection',{}).get('index'))),flush=True)
 for n,h in hashes.items():assert inputs.sha(HERE/n)==h,n
 inputs.write(HERE/'model_test'/(g+'_completion.json'),dict(complete=True,hashes=hashes,worker=socket.gethostname()))
if __name__=='__main__':main()
