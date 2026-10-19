"""Use the existing validation split to admit a recurrence model by full cost."""
from s00_fast_common import *
import subprocess,signal,traceback
from s06_train import cases
from s01_fast_recurrence import reduce as recurrence
DEP=HERE/'deployment'
old=legacy();h=old.h
helpers=h.inputs.module('fast_gate_helpers',h.BLOCK/'s11_extension_test.py')
prior=h.inputs.module('fast_gate_prior_recurrence',PRIOR/'s00_recurrence.py')

def measure(c,m,rep,ref,phase):
 dest=DEP/phase/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
 if dest.exists():return read(dest)
 request=HERE/'requests'/('gate_'+c['id']+'_'+m+'.json');write(request,c)
 isold=m=='previous';output=(PRIOR if isold else HERE)/'requests'/('gate_'+c['id']+'_'+m+'.pending.gz')
 script=PRIOR/'s10_runtime.py' if isold else HERE/'s12_deploy.py'
 cmd=[sys.executable,str(script),'--case',str(request),'--output',str(output),'--method','learned' if isold else m]
 start=time.perf_counter();proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,env=dict(os.environ,**({'KIRA_FAST_EXACT_ONLY':'1'} if phase=='validation' else {})))
 try:
  stdout,stderr=proc.communicate(timeout=125);r=read(output) if output.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1000:]
 except subprocess.TimeoutExpired:
  for pid in helpers.descendants(proc.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  proc.communicate();r=dict(success=False,status='application_deadline')
 finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
 elapsed=time.perf_counter()-start;ok,n=h.compare(r,ref)
 r.update(case=c['id'],method=m,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=elapsed,complete_process_and_check_seconds=time.perf_counter()-start)
 write(dest,r);return r

def main():
 import numpy as np
 cs=cases(2621,'validation');rows=[]
 for i,c in enumerate(cs):
  # Verify that this additional job needs no native solver or native scratch.
  refpath=DEP/'validation_references'/(c['id']+'.json.gz')
  if refpath.exists():ref=read(refpath)
  else:
   raw=prior.reduce(c,deadline=time.perf_counter()+120);assert raw is not None,('Reference preparation limit',c['id'])
   reference=admit(c,raw);probe=admit(c,recurrence(c,deadline=time.perf_counter()+10,backend='gmp',pivot='last'))
   assert reference is not None and probe is not None and h.equal(reference['coefficients'],probe['coefficients'])[0]
   ref=dict(success=True,blocks=[dict(indices=list(range(len(c['definition']['propagators']))),case=c,result=reference)])
   write(refpath,ref)
  times={m:[] for m in ['candidate','fixed_recurrence']}
  for rep in range(3):
   order=['candidate','fixed_recurrence'] if (i+rep)%2==0 else ['fixed_recurrence','candidate']
   for m in order:
    r=measure(c,m,rep,ref,'validation');assert r['independently_verified'],(c['id'],m)
    assert all(b['result'].get('route')=='one_loop_cayley_recurrence' for b in r['blocks'])
    times[m].append(r['complete_process_and_check_seconds'])
  rows.append(dict(case=c['id'],times=times));print(json.dumps(dict(case=c['id'],medians={m:statistics.median(v) for m,v in times.items()})),flush=True)
 x=np.array([r['times']['candidate'] for r in rows]);y=np.array([r['times']['fixed_recurrence'] for r in rows]);a=float(np.median(x,axis=1).sum());b=float(np.median(y,axis=1).sum());ix=np.random.RandomState(2887).randint(0,3,(2000,len(rows),3));ii=np.arange(len(rows))[None,:,None];rat=np.median(x[ii,ix],axis=2).sum(1)/np.median(y[ii,ix],axis=2).sum(1);ci=list(map(float,np.quantile(rat,[.025,.975])))
 enabled=a<.98*b and ci[1]<1
 v=dict(complete=True,enabled=enabled,requests=len(rows),candidate_seconds=a,fixed_recurrence_seconds=b,ratio=a/b,repeat_interval=ci,criterion='At least two percent lower complete median total and repetition interval below one on the original validation split.',rows=rows,model_sha256=sha(HERE/'trained_model/recurrence.json'),source_sha256={n:sha(HERE/n) for n in ['s12_deploy.py','s13_application_gate.py']},reserved_results_used_for_admission=False)
 write(DEP/'admission.json',v);print(json.dumps({k:v for k,v in v.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
