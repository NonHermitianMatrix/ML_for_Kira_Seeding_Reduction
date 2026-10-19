"""Compare full applications, then audit bounded coverage without hiding failures."""
from s00_fast_common import *
from s02_fast_formulas import reduce as formulas
import subprocess,signal,traceback
OLD=legacy();h=OLD.h
helpers=h.inputs.module('fast_reference_helpers',h.BLOCK/'s11_extension_test.py')
prior_prepare=h.inputs.module('fast_native_reference',PRIOR/'s04_prepare.py')

def reference(c):
 out=[];memo={}
 for part in split_blocks(c):
  sub=part['case'];key=json.dumps([sub['definition'],sub['targets']],sort_keys=True)
  if key not in memo:
   f=formulas(sub);r=None
   if f is not None:
    r=h.vacuum.reduce(sub,reference=True)
    if r is None:r=h.tensor.reduce(sub,reference=True)
    if r is None and f['route']=='finite_massless_propagator':r=helpers.gamma_reference(sub)
   if r is None and len(sub['definition']['loop_momenta'])==1:
    bs=OLD.basis(sub)
    a=prior_prepare.native(sub,bs,ordering=2);b=prior_prepare.native(sub,bs,ordering=1,expanded=False)
    ok,n=h.equal(a.get('coefficients',{}),b.get('coefficients',{})) if a['success'] and b['success'] else (False,0)
    r=dict(a,success=ok,coefficient_checks=n,second_check=b)
   elif r is None:
    ref=helpers.reference(sub);r=ref['blocks'][0]['result'] if ref['success'] else ref
   memo[key]=r
  out.append(dict(indices=part['indices'],case=sub,result=memo[key]))
 return dict(success=all(b['result']['success'] for b in out),blocks=out)

def measured(c,m,rep,ref=None,phase='model_test',limit=125):
 dest=HERE/phase/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
 if dest.exists():return read(dest)
 request=HERE/'requests'/(c['id']+'_'+m+'.json');write(request,c)
 old=m in ['previous','native'];script=PRIOR/'s10_runtime.py' if old else HERE/'s03_fast_runtime.py'
 output=(PRIOR if old else HERE)/'requests'/('fast_'+c['id']+'_'+m+'.pending.gz')
 command=[sys.executable,str(script),'--case',str(request),'--output',str(output),'--method','learned' if m=='previous' else m]
 start=time.perf_counter();p=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=p.communicate(timeout=limit);r=read(output) if output.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1000:]
 except subprocess.TimeoutExpired:
  for pid in helpers.descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
 elapsed=time.perf_counter()-start;ok,n=h.compare(r,ref) if ref and ref['success'] else (False,0)
 r.update(case=c['id'],method=m,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=elapsed,complete_process_and_check_seconds=time.perf_counter()-start);write(dest,r);return r

def main(worker):
 p=read(HERE/'protocol.json');assert p['complete'];assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items());assert sha(HERE/'trained_model/recurrence.json')==p['new_model_sha256'];assert sha(PRIOR/'basis_registry.json')==p['prior_basis_sha256']
 assert sha(OLD.PREVIOUS/'trained_model/freeze.json')==p['prior_model_sha256'];assert sha(OLD.PREVIOUS/'trained_model/expert.json')==p['prior_expert_sha256']
 for i,c in enumerate(p['timing']):
  if i%2!=worker:continue
  dest=HERE/'coverage'/(c['id']+'.json')
  if dest.exists():continue
  start=time.perf_counter()
  try:ref=reference(c)
  except Exception as e:ref=dict(success=False,status='reference_exception',error=repr(e),traceback=traceback.format_exc()[-1000:])
  ref['preparation_seconds']=time.perf_counter()-start;write(HERE/'references'/(c['id']+'.json.gz'),ref);first={}
  for rep in range(3):
   methods=p['methods'];order=methods[(i+rep)%4:]+methods[:(i+rep)%4]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measured(c,m,rep,ref)
    if not rep:first[m]=r
  row=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],reference_success=ref['success'],reference_seconds=ref['preparation_seconds'],verified={m:r['independently_verified'] for m,r in first.items()},seconds={m:r['complete_process_and_check_seconds'] for m,r in first.items()});write(dest,row);print(json.dumps(row),flush=True)
 write(HERE/f'timing_{worker}_complete.json',dict(complete=True))
 for i,c in enumerate(p['coverage']):
  if i%2!=worker:continue
  dest=HERE/'audit'/(c['id']+'.json')
  if dest.exists():continue
  # Audit timers are distinct from the full-workflow speed comparisons.
  order=['learned','previous'] if i%4<2 else ['previous','learned'];rs={m:measured(c,m,0,None,'audit_records',20) for m in order}
  ok,n=h.compare(rs['learned'],rs['previous']) if all(r['success'] for r in rs.values()) else (False,0)
  row=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],indices=len(c['definition']['propagators']),paired_verified=ok,coefficient_checks=n,methods={m:dict(success=r['success'],status=r['status'],seconds=r['application_seconds'],block_statuses=[b['result']['status'] for b in r.get('blocks',[])],routes=[b['result'].get('route') for b in r.get('blocks',[])]) for m,r in rs.items()});write(dest,row);print(json.dumps(dict(audit=c['id'],success={m:r['success'] for m,r in rs.items()},paired_verified=ok)),flush=True)
 write(HERE/f'worker_{worker}_complete.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
