"""Test the corrected interface on fresh parameters after basis calibration."""
from s00_common import *
import subprocess,signal,traceback
from s01_families import connected,products,split_blocks
from s04_checks import compare,gamma_reference
from s09_extension import exact_cases,EXT
from s03_runtime import formula
import s07_exact_vacuum as vacuum
import s16_massless_tensor as tensor
from s17_massless_checks import cases as massless_cases

def descendants(pid):
 pending=[pid];found=set()
 while pending:
  current=pending.pop()
  if current in found:continue
  found.add(current)
  try:
   for task in (Path('/proc')/str(current)/'task').iterdir():
    try:pending.extend(map(int,(task/'children').read_text().split()))
    except (OSError,ValueError):pass
  except OSError:pass
 return found

def initialize():
 if (EXT/'protocol.json').exists():return READ(EXT/'protocol.json')
 assert READ(EXT/'setup_complete.json')['complete']
 cases=[c for c in connected(1601,'reserved') if len(c['definition']['loop_momenta'])<=3]+products(1607,'reserved')
 cases += [c for c in exact_cases() if len(c['definition']['loop_momenta'])>=4]
 cases += [c for c in massless_cases() if len(c['definition']['loop_momenta'])>=4]
 d=dict(allocation='Exclusive case claims; all methods and repetitions for one case stay on one worker.',complete=True,cases=cases,repetitions=3,methods=['native','fixed','learned'],model_sha256=sha(EXT/'deployment/freeze.json'),basis_sha256=sha(EXT/'basis_cache.json'),source_sha256={n:sha(HERE/n) for n in ['s07_exact_vacuum.py','s08_reduce.py','s10_validated_runtime.py','s11_extension_test.py','s16_massless_tensor.py']},scope='Fresh physical parameters after canonical-basis correction. Analytic targets were checked before timing and do not enter model selection.')
 write(EXT/'protocol.json',d);return d

def reference(c):
 parts=split_blocks(c);cache=READ(EXT/'basis_cache.json');out=[];memo={}
 for part in parts:
  sub=part['case'];d=sub['definition'];signature=json.dumps([d['loop_momenta'],d['external_momenta'],d['propagators'],d['scalarproduct_rules'],sub['targets']],sort_keys=True)
  if signature in memo:r=memo[signature]
  else:
   r=vacuum.reduce(sub,reference=True)
   if r is None:r=tensor.reduce(sub,reference=True)
   if r is None:
    f=formula(sub)
    if f and f['route']=='massless_scalar_recurrence':r=gamma_reference(sub)
    else:
     entry=cache['entries'].get(key(sub));basis=restore_basis(sub,entry['basis']) if entry else ([[1]] if f else None)
     trials=[]
     for a in ['expanded','native']:
      with rt.environment():
       os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
       r=rt.native.run(sub,sub['size'],'native',HERE/'unused',timeout=45,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=inputs.bounds(sub,a),ordering=2,threads=1)
      r=rt.compact(r);trials.append(r)
      if r['success']:break
     r=dict(r,reference_attempts=trials)
   memo[signature]=r
  out.append(dict(indices=part['indices'],case=sub,result=r))
  if not r['success']:return dict(success=False,status=r['status'],blocks=out)
 return dict(success=True,status='reference_completed',blocks=out)

def measured(c,m,rep,ref):
 dest=EXT/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
 if dest.exists():return READ(dest)
 request=EXT/'requests'/(c['id']+'_'+m+'.json');pending=request.with_suffix('.pending.gz');write(request,c)
 cmd=[sys.executable,str(HERE/('s03_runtime.py' if m=='before' else 's08_reduce.py')),'--case',str(request),'--output',str(pending),'--method','learned' if m=='before' else m]
 begin=time.perf_counter();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=p.communicate(timeout=125);r=READ(pending) if pending.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1200:]
 except subprocess.TimeoutExpired:
  for pid in descendants(p.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
 finally:request.unlink(missing_ok=True);pending.unlink(missing_ok=True)
 process_seconds=time.perf_counter()-begin
 ok,n=compare(r,ref) if ref['success'] else (False,0)
 r.update(case=c['id'],method=m,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=process_seconds,complete_process_and_check_seconds=time.perf_counter()-begin)
 write(dest,r);return r

def main(worker):
 protocol=initialize();assert protocol['model_sha256']==sha(EXT/'deployment/freeze.json')
 assert protocol['basis_sha256']==sha(EXT/'basis_cache.json')
 assert all(sha(HERE/n)==v for n,v in protocol['source_sha256'].items())
 for i,c in enumerate(protocol['cases']):
  cover=EXT/'coverage'/(c['id']+'.json')
  if cover.exists():continue
  claim=EXT/'claims'/(c['id']+'.json');claim.parent.mkdir(exist_ok=True)
  try:
   fd=os.open(claim,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
   with os.fdopen(fd,'w') as stream:json.dump(dict(worker=worker,job=os.environ.get('JOB_ID')),stream)
  except FileExistsError:continue
  start=time.perf_counter();f=EXT/'references'/(c['id']+'.json.gz')
  if f.exists():ref=READ(f)
  else:
   try:ref=reference(c)
   except Exception as e:ref=dict(success=False,status='reference_exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
   ref['preparation_seconds']=time.perf_counter()-start;write(f,ref)
  methods=['native','fixed','learned']
  if c['scope']=='coupled_family' or (c['scope'] in ['analytic_vacuum','analytic_massless'] and len(c['definition']['loop_momenta'])<=7):methods.append('before')
  first={}
  for rep in range(3):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measured(c,m,rep,ref)
    if not rep:first[m]=r
  row=dict(case=c['id'],loops=len(c['definition']['loop_momenta']),scope=c['scope'],family=c['topology_group'],reference_success=ref['success'],reference_status=ref.get('status'),methods={m:dict(completed=r['success'],verified=r['independently_verified'],status=r.get('status'),seconds=r['complete_process_and_check_seconds'],model_used=r.get('model_used',False)) for m,r in first.items()},elapsed_seconds=time.perf_counter()-start)
  write(cover,row);print(json.dumps(dict(case=c['id'],verified={m:r['independently_verified'] for m,r in first.items()},seconds=row['elapsed_seconds'])),flush=True)
 write(EXT/('worker_'+str(worker)+'_complete.json'),dict(complete=True,worker=worker,protocol_sha256=sha(EXT/'protocol.json'),model_sha256=sha(EXT/'deployment/freeze.json')));print('EXTENSION WORKER COMPLETE',worker,flush=True)

if __name__=='__main__':main(int(sys.argv[1]))
