"""Fresh-process comparisons on the frozen thirteen-loop coverage grid."""
from s00_common import *
import signal,subprocess,traceback
from s01_families import split_blocks,initialize
from s04_checks import reference,compare

def descendants(pid):
 pending=[pid];found=set()
 while pending:
  p=pending.pop()
  if p in found:continue
  found.add(p)
  try:
   for task in (Path('/proc')/str(p)/'task').iterdir():
    try:pending.extend(map(int,(task/'children').read_text().split()))
    except (OSError,ValueError):pass
  except OSError:pass
 return found

def measured(c,method,rep,ref):
 dest=HERE/'model_test'/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
 if dest.exists():return READ(dest)
 request=HERE/'requests'/(c['id']+'_'+method+'.json');out=request.with_suffix('.pending.gz');write(request,c)
 if method=='previous':
  command=[sys.executable,str(general.HERE/'s22_reduce.py'),'--case',str(request),'--output',str(out)]
 else:command=[sys.executable,str(HERE/'s03_runtime.py'),'--case',str(request),'--output',str(out),'--method',method]
 tick=time.perf_counter();process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=process.communicate(timeout=125)
  r=READ(out) if out.exists() else dict(success=False,status='missing_application_output')
  if method=='previous' and r.get('success'):
   parts=split_blocks(c)
   if len(parts)!=1:r=dict(success=False,status='previous_output_requires_basis_conversion',previous=r)
   else:r=dict(r,blocks=[dict(indices=parts[0]['indices'],case=parts[0]['case'],result=r)],model_used=r.get('model_used',False))
  r['process_returncode']=process.returncode;r['stderr_tail']=stderr.decode(errors='replace')[-1800:]
 except subprocess.TimeoutExpired:
  children=descendants(process.pid)
  for pid in children:
   try:os.kill(pid,signal.SIGTERM)
   except ProcessLookupError:pass
  try:process.communicate(timeout=2)
  except subprocess.TimeoutExpired:
   for pid in children:
    try:os.kill(pid,signal.SIGKILL)
    except ProcessLookupError:pass
   process.communicate()
  r=dict(success=False,status='application_deadline')
 finally:
  request.unlink(missing_ok=True);out.unlink(missing_ok=True)
 process_seconds=time.perf_counter()-tick
 ok,checks=compare(r,ref) if ref.get('success') else (False,0)
 r.update(case=c['id'],method=method,rep=rep,application_seconds=process_seconds,complete_process_and_check_seconds=time.perf_counter()-tick,independently_verified=ok,coefficient_checks=checks,reference_available=ref.get('success',False))
 write(dest,r);return r

def main(worker):
 initialize();checks=READ(HERE/'checks/summary.json');assert checks['complete'];f=READ(HERE/'trained_model/freeze.json');assert f['complete']
 assert all(sha(HERE/n)==h for n,h in checks['source_sha256'].items())
 assert checks['model_sha256']==sha(HERE/'trained_model/freeze.json') and checks['cache_sha256']==sha(HERE/'basis_cache.json')
 protocol=READ(HERE/'protocol.json');cases=protocol['cases'];counts={}
 for i,c in enumerate(cases):
  if i%2!=worker:continue
  cover=HERE/'coverage'/(c['id']+'.json')
  if cover.exists():continue
  start=time.perf_counter();refpath=HERE/'references'/(c['id']+'.json.gz')
  if refpath.exists():ref=READ(refpath)
  else:
   try:ref=reference(c)
   except Exception as e:ref=dict(success=False,status='reference_exception',error=repr(e),traceback=traceback.format_exc()[-1600:])
   ref['preparation_seconds']=time.perf_counter()-start;write(refpath,ref)
  methods=['native','fixed','learned']+(['previous'] if c['scope']=='coupled_family' else [])
  # Rotate fresh processes on the same worker. Never retry failed tests until pass.
  order=methods[i%len(methods):]+methods[:i%len(methods)];first={}
  for m in order:first[m]=measured(c,m,0,ref)
  for rep in [1,2]:
   rotated=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for m in rotated:
    if first[m]['independently_verified']:measured(c,m,rep,ref)
  record=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],family=c['topology_group'],reference_success=ref['success'],reference_status=ref.get('status'),methods={m:dict(completed=r.get('success',False),verified=r['independently_verified'],status=r.get('status'),seconds=r['complete_process_and_check_seconds'],model_used=r.get('model_used',False)) for m,r in first.items()},elapsed_seconds=time.perf_counter()-start)
  write(cover,record);counts[c['scope']]=counts.get(c['scope'],0)+1
  print(json.dumps(dict(worker=worker,case=c['id'],loops=record['loops'],reference=ref['success'],verified={m:r['independently_verified'] for m,r in first.items()},elapsed=record['elapsed_seconds'])),flush=True)
 write(HERE/('worker_'+str(worker)+'_complete.json'),dict(complete=True,worker=worker,model_sha256=sha(HERE/'trained_model/freeze.json'),protocol_sha256=sha(HERE/'protocol.json')))
 print('WORKER COMPLETE',worker,flush=True)

if __name__=='__main__':main(int(sys.argv[1]))
