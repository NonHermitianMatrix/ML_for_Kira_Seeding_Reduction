"""Measure complete candidate costs on fresh training and validation inputs."""
from s00_cost_common import *
import subprocess,signal,traceback
from s11_extension_test import reference,descendants

def cases(profile,split):
 out=[]
 for rank in [2,3,4]:
  for shape in ['first','second']+(['distributed'] if rank>2 else []):
   c=canonical(inputs.case('nonplanar_box',profile,'rank'+str(rank),split));a=[1]*7+[0,0]
   if shape=='distributed':a[7:]=[-((rank+1)//2),-(rank//2)]
   else:a[7 if shape=='first' else 8]=-rank
   c.update(id=f'nonplanar_h{profile}_{shape}_r{rank}',targets=[a],size=1,shape=shape,scope='coupled_family',topology_group='nonplanar_box',split=split)
   assert eligible(c);out.append(c)
 return out

def initialize():
 p=HERE/'protocol.json'
 if p.exists():return READ(p)
 assert READ(BASE/'trained_model/freeze.json')['enabled'] is False
 expert=READ(SPARSE/'trained_model/cost_nonplanar_box.json');assert expert['enabled']
 raw=inputs.case('nonplanar_box',2301,'rank2','template');assert inputs.signature(raw)==expert['signature']
 write(HERE/'trained_model/expert.json',expert)
 native_action=geometry.action(raw)
 write(HERE/'trained_model/sparse_fixed.json',dict(theta=expert['candidates'][expert['fixed_index']],native_action=native_action))
 d=dict(training=cases(2301,'training')+cases(2303,'training'),validation=cases(2309,'validation'),actions=ACTIONS,training_repetitions=1,validation_repetitions=2,basis_sha256=sha(BLOCK/'extension/basis_cache.json'),expert_source_sha256=sha(SPARSE/'trained_model/cost_nonplanar_box.json'),base_model_sha256=sha(BASE/'trained_model/freeze.json'),expert_sources={n:sha(SPARSE/n) for n in ['s00_policy.py','s05_reduce.py']},scope='Single nonplanar two-loop targets, unit physical powers, numerator ranks 2 through 4. Other blocks retain the prior complete-time application.',limits=dict(native_call_seconds=45,request_seconds=110,outer_seconds=125,scratch_bytes=32*1024**2,seed_input_bytes=4*1024**2,concurrency=2))
 write(p,d);print(json.dumps(dict(training=len(d['training']),validation=len(d['validation']))),flush=True);return d

def measured(c,method,rep,ref,folder):
 dest=HERE/folder/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
 if dest.exists():return READ(dest)
 req=HERE/'requests'/(c['id']+'_'+method+'.json');out=req.with_suffix('.pending.gz');write(req,c)
 script=BASE/'s01_runtime.py' if method=='previous' else HERE/'s01_runtime.py'
 if method=='previous':out=BASE/'requests'/('hybrid_'+c['id']+'.pending.gz')
 cmd=[sys.executable,str(script),'--case',str(req),'--output',str(out),'--method','learned' if method=='previous' else method]
 start=time.perf_counter();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=p.communicate(timeout=125);r=READ(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1000:]
 except subprocess.TimeoutExpired:
  for pid in descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:
  remove(req)
  if method=='previous':out.unlink(missing_ok=True)
  else:remove(out)
 process=time.perf_counter()-start;ok,n=compare(r,ref) if ref['success'] else (False,0)
 r.update(case=c['id'],method=method,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=process,complete_process_and_check_seconds=time.perf_counter()-start)
 write(dest,r);return r

def get_reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if p.exists():return READ(p)
 start=time.perf_counter()
 try:r=reference(c)
 except Exception as e:r=dict(success=False,status='reference_exception',error=repr(e),traceback=traceback.format_exc()[-1000:])
 r['preparation_seconds']=time.perf_counter()-start;write(p,r);return r

def claim(c,phase,worker):
 p=HERE/'claims'/phase/(c['id']+'.json');p.parent.mkdir(parents=True,exist_ok=True)
 try:
  with p.open('x') as f:json.dump(dict(worker=worker,job=os.environ.get('JOB_ID')),f)
  return True
 except FileExistsError:return False

def main(worker):
 protocol=initialize()
 if worker==99:os.environ['HYBRID_SEED_AUDIT']='1'
 if worker!=99:assert READ(HERE/'pilot_validation.json')['complete']
 for phase in ['training','validation']:
  if worker==99 and phase!='training':break
  selected_cases=protocol[phase][:1] if worker==99 else protocol[phase]
  for i,c in enumerate(selected_cases):
   folder='pilot' if worker==99 else phase
   done=HERE/'coverage'/folder/(c['id']+'.json')
   if done.exists() or not claim(c,folder,worker):continue
   start=time.perf_counter();ref=get_reference(c);records=[]
   for rep in range(protocol[phase+'_repetitions']):
    for j in range(len(ACTIONS)):
     a=ACTIONS[(i+rep+j)%len(ACTIONS)];r=measured(c,a,rep,ref,folder)
     records.append(dict(action=a,rep=rep,verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'],failed_attempts=r.get('failed_attempts',0)))
   if worker==99:
    results=[READ(HERE/folder/(c['id']+'_'+a+'_r0.json.gz')) for a in ACTIONS]
    gate=any(a.get('seed_audit') is not None for r in results for b in r.get('blocks',[]) for a in b['result'].get('attempts',[]))
    write(HERE/'pilot_validation.json',dict(complete=all(r['independently_verified'] for r in results) and gate,seed_gate_observed=gate,case=c['id']))
    assert READ(HERE/'pilot_validation.json')['complete'],'Pilot exact checks or native seed gate failed'
   write(done,dict(case=c['id'],reference_success=ref['success'],records=records,seconds=time.perf_counter()-start))
   print(json.dumps(dict(phase=phase,case=c['id'],reference=ref['success'],seconds=time.perf_counter()-start)),flush=True)
 write(HERE/('collect_'+str(worker)+'_complete.json'),dict(complete=True))
if __name__=='__main__':main(99 if sys.argv[1]=='pilot' else int(sys.argv[1]))
