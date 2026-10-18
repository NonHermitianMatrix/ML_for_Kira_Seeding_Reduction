"""Validate the parser guard, then test fresh symbolic powers and compatibility."""
from s01_common import *
from s03_cases import polygon
from s04_prepare import native,reference_old
import subprocess,signal,statistics,copy
helper=h.inputs.module('parser_guard_process',h.BLOCK/'s11_extension_test.py')
DEP=HERE/'deployment'

def symbolic(a,name,L=1):
 c=polygon(2,2501,1,True);c.update(id=name,targets=[a],size=1,scope='symbolic_guard',split='reserved')
 if L>1:
  families=h.inputs.module('guard_families',h.BLOCK/'s01_families.py');c=families.compose([c]*L,name,'reserved');c['scope']='symbolic_guard'
 return c

def cases():
 cs=[symbolic([3,2],'guard_symbolic_32'),symbolic([2,3],'guard_symbolic_23'),symbolic([3,2],'guard_symbolic_product_L2',2),symbolic([2,3],'guard_symbolic_product_L13',13)]
 cs += [polygon(n,2521,3) for n in [2,4,5]]
 for c in cs[4:]:c['scope']='guard_compatibility'
 c=canonical_case=h.canonical(h.inputs.case('nonplanar_box',2527,'rank3','reserved'));c.update(scope='guard_compatibility',id='guard_nonplanar_h2527',targets=[[1]*7+[-3,0]],size=1);cs.append(c)
 c=h.canonical(h.gen.case('vacuum_one_mass',13,False,2531));P=c['definition']['physical_propagators'];N=len(c['definition']['propagators']);a=[1]*P+[0]*(N-P);a[0]+=2;c.update(scope='guard_compatibility',id='guard_vacuum_L13',targets=[a],size=1);cs.append(c)
 return cs

def reference(c):
 out=[];memo={}
 for part in h.split_blocks(c):
  sub=part['case'];key=json.dumps([sub['definition'],sub['targets']],sort_keys=True)
  if key not in memo:
   if len(sub['definition']['loop_momenta'])==1:
    bs=basis(sub);assert bs is not None
    a=native(sub,bs,ordering=2);b=native(sub,bs,ordering=1,expanded=False)
    ok,n=h.equal(a.get('coefficients',{}),b.get('coefficients',{})) if a['success'] and b['success'] else (False,0)
    r=dict(a,success=ok,coefficient_checks=n,second_check=b)
   else:
    ref=reference_old(sub);r=ref['blocks'][0]['result'] if ref['success'] else ref
   memo[key]=r
  out.append(dict(indices=part['indices'],case=sub,result=memo[key]))
 return dict(success=all(b['result']['success'] for b in out),blocks=out)

def measured(c,m,rep,ref,phase):
 dest=DEP/phase/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
 if dest.exists():return READ(dest)
 req=HERE/'requests'/('guard_'+c['id']+'_'+m+'.json');out=req.with_suffix('.pending.gz');write(req,c)
 script=HERE/('s02_runtime.py' if m=='all_analytic' else 's10_runtime.py')
 cmd=[sys.executable,str(script),'--case',str(req),'--output',str(out),'--method','learned' if m=='all_analytic' else m]
 start=time.perf_counter();proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  stdout,stderr=proc.communicate(timeout=125);r=READ(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=stderr.decode(errors='replace')[-1000:]
 except subprocess.TimeoutExpired:
  for pid in helper.descendants(proc.pid):
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  proc.communicate();r=dict(success=False,status='application_deadline')
 finally:req.unlink(missing_ok=True);out.unlink(missing_ok=True)
 elapsed=time.perf_counter()-start;ok,n=h.compare(r,ref) if ref['success'] else (False,0)
 r.update(case=c['id'],method=m,rep=rep,independently_verified=ok,coefficient_checks=n,application_seconds=elapsed,complete_process_and_check_seconds=time.perf_counter()-start);write(dest,r);return r

def initialize():
 dev=[symbolic([4,1],'guard_development_41'),symbolic([1,4],'guard_development_14')];rows=[]
 for i,c in enumerate(dev):
  ref=reference(c);assert ref['success'];write(DEP/'development_references'/(c['id']+'.json.gz'),ref)
  times={m:[] for m in ['learned','all_analytic']}
  for rep in range(3):
   for m in (['learned','all_analytic'] if (i+rep)%2 else ['all_analytic','learned']):
    r=measured(c,m,rep,ref,'development');assert r['independently_verified'];times[m].append(r['complete_process_and_check_seconds'])
  rows.append(times)
 a=sum(statistics.median(r['learned']) for r in rows);b=sum(statistics.median(r['all_analytic']) for r in rows);assert a<.95*b,(a,b)
 write(DEP/'admission.json',dict(complete=True,enabled=True,development_cases=dev,gated_seconds=a,all_analytic_seconds=b,ratio=a/b,rule='Preserve old exact formulas. Admit the new recurrence only for direct rational mass and scalar-product values; otherwise use existing native Kira.'))
 cs=cases();assert len(cs)==9
 # Every one-loop target has the already prepared basis. No registry mutation.
 for c in cs:
  for part in h.split_blocks(c):
   if len(part['case']['definition']['loop_momenta'])==1:assert basis(part['case']) is not None
 protocol=dict(cases=cs,methods=['learned','fixed','native','all_analytic'],repetitions=3,runtime_sources={n:sha(HERE/n) for n in ['s00_recurrence.py','s01_common.py','s02_runtime.py','s10_runtime.py','s11_guard_test.py']},basis_sha256=sha(HERE/'basis_registry.json'),initial_protocol_sha256=sha(HERE/'test_protocol.json'),scope='Four fresh symbolic requests with mixed powers (3,2) and (2,3), including independent products, plus five compatibility requests. Development uses different powers (4,1) and (1,4).')
 write(DEP/'protocol.json',protocol)

def test(worker):
 p=READ(DEP/'protocol.json');assert READ(DEP/'admission.json')['enabled'];assert all(sha(HERE/n)==h0 for n,h0 in p['runtime_sources'].items());assert sha(HERE/'basis_registry.json')==p['basis_sha256']
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=DEP/'coverage'/(c['id']+'.json')
  if dest.exists():continue
  start=time.perf_counter();ref=reference(c);ref['preparation_seconds']=time.perf_counter()-start;write(DEP/'references'/(c['id']+'.json.gz'),ref)
  first={}
  for rep in range(3):
   order=p['methods'][(i+rep)%4:]+p['methods'][:(i+rep)%4]
   for m in order:
    if rep and not first[m]['independently_verified']:continue
    r=measured(c,m,rep,ref,'model_test')
    if not rep:first[m]=r
  write(dest,dict(case=c['id'],scope=c['scope'],verified={m:r['independently_verified'] for m,r in first.items()},reference_seconds=ref['preparation_seconds']))
  print(json.dumps(dict(case=c['id'],verified={m:r['independently_verified'] for m,r in first.items()})),flush=True)
 write(DEP/f'test_{worker}_complete.json',dict(complete=True))
if __name__=='__main__':initialize() if sys.argv[1]=='initialize' else test(int(sys.argv[1]))
