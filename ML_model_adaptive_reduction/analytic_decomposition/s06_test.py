"""Fresh-process timings with exact checks and unchanged learned models."""
from s01_common import *
import subprocess,signal,statistics,traceback
from s04_prepare import reference_old
helpers=h.inputs.module('analytic_process_helpers',h.BLOCK/'s11_extension_test.py')

def measured(c,method,rep,ref):
 dest=HERE/'model_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
 if dest.exists():return READ(dest)
 req=HERE/'requests'/(c['id']+'_'+method+'.json');out=req.with_suffix('.pending.gz');write(req,c)
 script=PREVIOUS/'s01_runtime.py' if method=='previous' else HERE/'s02_runtime.py'
 if method=='previous':out=PREVIOUS/'requests'/('analytic_'+c['id']+'.pending.gz')
 cmd=[sys.executable,str(script),'--case',str(req),'--output',str(out),'--method','learned' if method=='previous' else method]
 start=time.perf_counter();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=p.communicate(timeout=125);r=READ(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1200:]
 except subprocess.TimeoutExpired:
  for pid in helpers.descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:req.unlink(missing_ok=True);out.unlink(missing_ok=True)
 seconds=time.perf_counter()-start;ok,n=h.compare(r,ref) if ref['success'] else (False,0)
 r.update(case=c['id'],method=method,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=seconds,complete_process_and_check_seconds=time.perf_counter()-start)
 write(dest,r);return r

def freeze():
 for i in range(2):assert READ(HERE/f'prepare_{i}_complete.json')['complete']
 (HERE/'.storage_bytes').unlink(missing_ok=True)
 p=READ(HERE/'protocol.json');p['runtime_sources']={n:sha(HERE/n) for n in ['s00_recurrence.py','s01_common.py','s02_runtime.py','s03_cases.py','s04_prepare.py','s06_test.py']};p['basis_sha256']=sha(HERE/'basis_registry.json');p['frozen']=True;write(HERE/'test_protocol.json',p)

def main(worker):
 p=READ(HERE/'test_protocol.json');assert p['frozen'];assert all(sha(HERE/n)==s for n,s in p['runtime_sources'].items());assert sha(HERE/'basis_registry.json')==p['basis_sha256']
 assert sha(PREVIOUS/'trained_model/freeze.json')==p['prior_model_sha256'];assert sha(PREVIOUS/'trained_model/expert.json')==p['prior_expert_sha256']
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'coverage'/(c['id']+'.json')
  if dest.exists():continue
  ref=READ(HERE/'references'/(c['id']+'.json.gz'));first={};start=time.perf_counter()
  for rep in range(3):
   methods=p['methods'];order=methods[(i+rep)%4:]+methods[:(i+rep)%4]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measured(c,m,rep,ref)
    if not rep:first[m]=r
  write(dest,dict(case=c['id'],scope=c['scope'],loops=len(c['definition']['loop_momenta']),reference_success=ref['success'],reference_seconds=ref['preparation_seconds'],first={m:dict(verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'],status=r['status']) for m,r in first.items()}))
  print(json.dumps(dict(case=c['id'],verified={m:r['independently_verified'] for m,r in first.items()},seconds=time.perf_counter()-start)),flush=True)
 write(HERE/f'test_{worker}_complete.json',dict(complete=True))
if __name__=='__main__':freeze() if sys.argv[1]=='freeze' else main(int(sys.argv[1]))
