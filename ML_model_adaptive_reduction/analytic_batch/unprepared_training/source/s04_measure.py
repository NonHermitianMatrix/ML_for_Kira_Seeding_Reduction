"""Independent native references and fresh-process timing."""
from s00_batch_common import *
import subprocess,signal,traceback

def native(h,c,basis,ordering=2,expanded=False):
 with h.rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  return h.rt.compact(h.rt.native.run(c,c['size'],'native',HERE/'unused',timeout=45,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=h.inputs.bounds(c,'expanded' if expanded else 'native'),ordering=ordering,threads=1))

def reference(c):
 old=legacy();h=old.h;blocks=[];memo={}
 for part in support.split_blocks(c):
  sub=part['case'];identity=json.dumps([sub['definition'],sub['targets']],sort_keys=True)
  if identity not in memo:
   d=sub['definition']
   if len(d['loop_momenta'])==1 and len(d['propagators'])==3 and all(p['mass_squared']=='0' for p in d['propagators']):
    # Independent native IBP, with the off-shell bubble protected as master.
    bs=[[1,0,1]];a=native(h,sub,bs,ordering=2,expanded=True);b=native(h,sub,bs,ordering=1,expanded=False)
    ok,n=h.equal(a.get('coefficients',{}),b.get('coefficients',{})) if a['success'] and b['success'] else (False,0)
    r=dict(a,success=ok,coefficient_checks=n,reference_check=b)
   elif eligible(sub):
    bs=support.basis(sub);a=native(h,sub,bs,ordering=2,expanded=False)
    if not a['success']:a=native(h,sub,bs,ordering=2,expanded=True)
    r=a
   else:
    e=h.inputs.module('batch_old_reference',h.BLOCK/'s11_extension_test.py');ref=e.reference(sub);r=ref['blocks'][0]['result'] if ref['success'] else ref
   memo[identity]=r
  blocks.append(dict(case=sub,indices=part['indices'],result=memo[identity]))
  if not memo[identity]['success']:break
 return dict(success=len(blocks)==len(support.split_blocks(c)) and all(b['result']['success'] for b in blocks),blocks=blocks)

def measured(c,method,rep,ref,phase,limit=125):
 dest=HERE/phase/(c['id']+'_'+method+'_r'+str(rep)+'.json.gz')
 if dest.exists():return read(dest)
 request=HERE/'requests'/(c['id']+'_'+method+'.json');old=method=='previous';output=(PREVIOUS if old else HERE)/'requests'/('analytic_batch_'+c['id']+'_'+method+'.pending.gz');write(request,c)
 script=PREVIOUS/'s12_deploy.py' if old else HERE/'s02_batch_runtime.py'
 tick=time.perf_counter();p=subprocess.Popen([sys.executable,str(script),'--case',str(request),'--output',str(output),'--method','final' if old else method],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,stderr=p.communicate(timeout=limit);r=read(output) if output.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-900:]
 except subprocess.TimeoutExpired:
  h=legacy().h;helper=h.inputs.module('batch_process_limits',h.BLOCK/'s11_extension_test.py')
  for pid in helper.descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:request.unlink(missing_ok=True);output.unlink(missing_ok=True)
 elapsed=time.perf_counter()-tick;ok,n=legacy().h.compare(r,ref) if ref['success'] else (False,0)
 r.update(case=c['id'],method=method,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=elapsed,complete_process_and_check_seconds=time.perf_counter()-tick)
 # Keep physics outputs and measured operations; omit repeated verbose logs.
 for block in r.get('blocks',[]):
  for a in block['result'].get('attempts',[]):a.pop('log_tail',None)
 write(dest,r);return r

def prepare(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if p.exists():return read(p)
 tick=time.perf_counter()
 try:r=reference(c)
 except Exception as e:r=dict(success=False,status='reference_exception',error=repr(e),traceback=traceback.format_exc()[-1000:])
 r['preparation_seconds']=time.perf_counter()-tick;write(p,r);return r
