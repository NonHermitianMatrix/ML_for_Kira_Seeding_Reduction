"""Compare complete reductions on the frozen native and analytic grids."""
from s00_reconstruction_common import *
from s06_measure import measured
from s20_reference import reference
import statistics,socket

def main(worker):
 protocol=read(HERE/'test_protocol.json.gz')
 assert all(sha(HERE/n)==digest for n,digest in protocol['source_sha256'].items())
 assert all(sha(HERE/'trained_model'/n)==digest for n,digest in protocol['model_sha256'].items())
 assert sha(TOOLS/'kira')==protocol['binary_sha256']
 old=previous();direct=load('reconstruction_exact_test',PREVIOUS/'s27_deploy_test.py')
 for i,c in enumerate(protocol['cases']):
  if i%2!=worker:continue
  dest=HERE/'model_test'/(c['id']+'.json.gz')
  if dest.exists():continue
  refpath=HERE/'test_references'/(c['id']+'.json.gz')
  if not refpath.exists():
   r=reference(c) if c['test_group']=='native' else direct.reference(c)
   write(refpath,r)
  ref=read(refpath)
  methods=protocol['methods'];times={m:[] for m in methods};success={m:[] for m in methods};saved={};checks=0;attempts={m:[] for m in methods};fallback={m:[] for m in methods};failures=[]
  for rep in range(protocol['repetitions']):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    r,t=measured(c,method,worker,protocol['seconds_per_application'],entry='s15_deploy.py')
    ok,n=direct.compare(c,r,ref) if ref.get('success') else (False,0)
    native=[a for b in r.get('blocks',[]) for a in b['result'].get('attempts',[])]
    failed=r.get('reconstruction_failed_attempt',{})
    native.extend(a for b in failed.get('blocks',[]) for a in b['result'].get('attempts',[]))
    times[method].append(t);success[method].append(ok);checks+=n;saved[method]=r
    attempts[method].append(sum(not a.get('success',False) for a in native))
    fallback[method].append(bool(r.get('reconstruction_fallback')))
    if not ok:failures.append(dict(method=method,repetition=rep,result=r))
    if ref.get('success') and r.get('success') and not ok:
     write(HERE/'disagreements'/(c['id']+'_'+method+str(rep)+'.json.gz'),dict(case=c,result=r,reference=ref))
     raise AssertionError((c['id'],method,'exact coefficient disagreement'))
  row=dict(case=c['id'],group=c['test_group'],topology=c.get('topology_group',c['test_group']),loops=len(c['definition']['loop_momenta']),targets=c['size'],worker_host=socket.gethostname(),reference_success=ref.get('success',False),times=times,success=success,failed_attempts=attempts,reconstruction_fallbacks=fallback,failed_applications=failures,median_seconds={m:statistics.median(v) for m,v in times.items()},checks=checks,results=saved)
  write(dest,row);print(c['id'],row['median_seconds'],{m:all(v) for m,v in success.items()},flush=True)
 write(HERE/f'test{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'test_protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
