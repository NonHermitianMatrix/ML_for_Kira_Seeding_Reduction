"""Measure the combined exact and learned application with matched controls."""
from s02_collect import *
import subprocess
METHODS=['native','previous','optimized_fixed','optimized_learned','optimized_application']
def main(w):
 f=read(HERE/'trained_model/freeze.json');assert f['application_sha256']==inputs.sha(HERE/'s01_application.py');assert read(HERE/'integration/completion.json')['complete']
 for n,h in f['model_sha256'].items():assert inputs.sha(HERE/'trained_model'/n)==h
 deployment=read(HERE/'trained_model/deployment.json');cases=make(deployment['reserved_profile'],'reserved');out=HERE/'combined_test';out.mkdir(exist_ok=True)
 frozen=dict(cases=cases,deployment_sha256=inputs.sha(HERE/'trained_model/deployment.json'),methods=METHODS,repetitions=5,models=f['model_sha256'],binary=inputs.sha(ROOT/'.tools/kira-sector-storage/kira'),wide_binary=inputs.sha(ROOT/'.tools/kira-sector-wide/kira'),storage_policy_sha256=inputs.sha(HERE/'integration/deployment.json'),source={n:inputs.sha(HERE/n) for n in ['s13_optimized.py','s14_combined_test.py']})
 fp=HERE/'combined_protocol.json'
 if fp.exists():assert read(fp)==frozen
 else:write(fp,frozen)
 for c in cases[w::2]:
  ref=reference(c);status_path=HERE/'combined_coverage'/(c['id']+'.json')
  if ref is None:write(status_path,dict(case=c['id'],status='reference_unavailable'));continue
  basis=read(ref)['masters'];failed=set()
  for rep in range(5):
   shift=(sum(c['id'].encode())+rep)%len(METHODS)
   for m in METHODS[shift:]+METHODS[:shift]:
    p=out/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
    if p.exists():
     if not read(p)['success']:failed.add(m)
     continue
    q=HERE/'requests'/(p.stem+'.json');write(q,dict(case=c,basis=basis,reference=str(ref),method=m));assert allocated()+2*1024**2<24*1024**2
    worker_output=p.with_name(p.name+'.pending.gz')
    start=time.perf_counter();proc=subprocess.run([str(ROOT/'.tools/seed-model/venv/bin/python'),str(HERE/'s13_optimized.py'),'--input',str(q),'--output',str(worker_output)],capture_output=True,timeout=310);elapsed=time.perf_counter()-start
    r=read(worker_output) if worker_output.exists() else dict(success=False,error=proc.stderr.decode()[-1500:]);r.update(complete_seconds=elapsed,case=c['id'],method=m,process_timer_complete=True);write(p,r);q.unlink()
    if worker_output.exists():worker_output.unlink()
    print(c['id'],m,r['success'],round(elapsed,3),flush=True)
    if not r['success']:failed.add(m)
  write(status_path,dict(case=c['id'],status='verified' if not failed else 'method_failed',failed_methods=sorted(failed),nontrivial=any(row and row!={t:'1'} for t,row in read(ref)['coefficients'].items())))
 write(HERE/('combined_'+str(w)+'_complete.json'),dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
