"""Independently test the first evolved seed boundary without a cost selector."""
import argparse,json,socket,time
from s03_train import reference
from s00_policy import *
def main():
 p=argparse.ArgumentParser();p.add_argument('graph');a=p.parse_args();g=a.graph
 f=HERE/'trained_model'/(g+'.json');freeze=rt.read(f);protocol=rt.read(HERE/'protocols'/(g+'.json'))
 hashes={n:inputs.sha(HERE/n) for n in ['s00_policy.py','s07_initial_test.py','trained_model/'+g+'.json']}
 outdir=HERE/'initial_test';outdir.mkdir(exist_ok=True)
 (outdir/'README.md').write_text('These reserved reductions test the initial evolved boundary.\nThey use different requests from the later cost-model test.\nThe initial model stays fixed during every comparison.\n')
 inputs.write(outdir/(g+'_freeze.json'),dict(hashes=hashes,cases=protocol['reserved'],repetitions=7,worker=socket.gethostname()))
 for i,c in enumerate(protocol['reserved']):
  refp,ref=reference(c)
  if not ref['success']:continue
  for rep in range(7):
   order=['native','fixed','learned'];k=(i+rep)%3;order=order[k:]+order[:k]
   for method in order:
    out=outdir/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
    if out.exists():continue
    start=time.perf_counter();theta=None
    if method!='native':
     fnow=rt.read(f);theta=fnow['theta'] if method=='learned' and fnow['enabled'] else fnow['fixed_theta']
    r=run(c,ref['masters'],theta,refp,timeout=90);r.update(method=method,complete_seconds=time.perf_counter()-start,repetition=rep,worker=socket.gethostname());save(out,r)
    print(json.dumps(dict(case=c['id'],method=method,seconds=r['complete_seconds'],success=r['success'],fallbacks=r['fallbacks'])),flush=True)
 for n,h in hashes.items():assert inputs.sha(HERE/n)==h,n
 inputs.write(outdir/(g+'_completion.json'),dict(complete=True,hashes=hashes))
if __name__=='__main__':main()
