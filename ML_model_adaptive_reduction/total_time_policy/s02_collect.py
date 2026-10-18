"""Measure complete candidate costs on fresh training and validation inputs."""
from s00_cost_common import *
import subprocess,signal,traceback
from s11_extension_test import reference,descendants

def cases(profile,split,shapes):
 out=[]
 for c0 in connected(profile,split):
  L=len(c0['definition']['loop_momenta']);g=c0['topology_group']
  if L>2 and not (L==3 and g in ['vacuum_all_mass_L3','propagator_massive_L3']):continue
  for shape in shapes:
   c=copy.deepcopy(c0);d=c['definition'];P=d['physical_propagators'];N=len(d['propagators']);ts=[]
   for j in range(min(P,3)):
    a=[int(i<P) for i in range(N)];i=(profile+j)%P
    if shape=='dots':a[i]+=1+(j==1)
    elif shape=='mixed':
     a[i]+=1
     if N>P:a[P+(profile+j)%(N-P)]=-1
    elif shape=='rank2':
     if N>P:a[P+(profile+j)%(N-P)]=-2
     else:a[i]+=2
    elif shape=='pinched':a[i]=0;a[(i+1)%P]+=1
    ts.append(a)
   c.update(id=c['id']+'_'+shape,targets=ts,size=len(ts),shape=shape,split=split)
   if exact(c) is None:out.append(c)
 return out

def initialize():
 p=HERE/'protocol.json'
 if p.exists():return READ(p)
 train=cases(1901,'training',['dots','mixed','rank2'])
 val=cases(1907,'validation',['dots','mixed'])
 # A whole graph is held out from every stage of model fitting and selection.
 train=[c for c in train if 'pentagon' not in c['topology_group']]
 val=[c for c in val if 'pentagon' not in c['topology_group']]
 d=dict(training=train,validation=val,actions=ACTIONS,training_repetitions=1,validation_repetitions=2,profile_scope='Fresh parameters and target patterns. Pentagon is a whole-graph holdout. High-loop factorable products test transfer of block decisions.',basis_sha256=sha(BLOCK/'extension/basis_cache.json'),parent_commit='ed8385f703e626a6f00c30f67e94a351a2d301b6',limits=dict(native_call_seconds=45,request_seconds=110,outer_seconds=125,scratch_bytes=32*1024**2,concurrency=2))
 write(p,d);print(json.dumps(dict(training=len(train),validation=len(val))),flush=True);return d

def measured(c,method,rep,ref,folder):
 dest=HERE/folder/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
 if dest.exists():return READ(dest)
 req=HERE/'requests'/(c['id']+'_'+method+'.json');out=req.with_suffix('.pending.gz');write(req,c)
 script=BLOCK/'s08_reduce.py' if method=='previous' else HERE/'s01_runtime.py'
 cmd=[sys.executable,str(script),'--case',str(req),'--output',str(out),'--method','learned' if method=='previous' else method]
 start=time.perf_counter();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=p.communicate(timeout=125);r=READ(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1000:]
 except subprocess.TimeoutExpired:
  for pid in descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:req.unlink(missing_ok=True);out.unlink(missing_ok=True)
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
 for phase in ['training','validation']:
  for i,c in enumerate(protocol[phase]):
   done=HERE/'coverage'/phase/(c['id']+'.json')
   if done.exists() or not claim(c,phase,worker):continue
   start=time.perf_counter();ref=get_reference(c);records=[]
   for rep in range(protocol[phase+'_repetitions']):
    for j in range(len(ACTIONS)):
     a=ACTIONS[(i+rep+j)%len(ACTIONS)];r=measured(c,a,rep,ref,phase)
     records.append(dict(action=a,rep=rep,verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'],failed_attempts=r.get('failed_attempts',0)))
   write(done,dict(case=c['id'],reference_success=ref['success'],records=records,seconds=time.perf_counter()-start))
   print(json.dumps(dict(phase=phase,case=c['id'],reference=ref['success'],seconds=time.perf_counter()-start)),flush=True)
 write(HERE/('collect_'+str(worker)+'_complete.json'),dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
