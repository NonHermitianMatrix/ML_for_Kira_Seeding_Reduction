"""Check fresh application launches and the previously published application."""
import argparse,json,os,signal,subprocess,sys,tempfile,time
from pathlib import Path
from s00_inputs import *
import s01_runtime as rt

def plan():
 p=HERE/'application_protocol.json'
 if not p.exists():
  inputs=rt.read(HERE/'protocol.json')['splits']['reserved'];wanted={(g,'dot' if g.startswith('bubble_box') else 'numerator' if g=='massless4' else 'dots') for g in GRAPHS}
  cs=[c for c in inputs if (c['topology_group'],c['shape']) in wanted and '_h515_' in c['id']]
  assert len(cs)==10
  write(p,dict(cases=cs,methods=['native','learned','previous'],repetitions=3,scope='Secondary fresh-process application comparison. Input parsing, imports, model loading, execution, serialization, process exit, and post-result coefficient checks are timed. References are prepared outside timing. No use in model selection.'))
 return rt.read(p)

def child(case_path,basis_path,out_path):
 c=rt.read(case_path);basis=rt.read(basis_path)
 import s24_parametric_runtime as previous
 start=time.perf_counter();app=previous.Reducer()
 try:r=app.reduce(c,basis)
 finally:app.close()
 r.update(complete_seconds=time.perf_counter()-start,reference_coefficients_supplied=False)
 rt.save(out_path,r)

def main():
 import statistics
 d=plan();assert rt.read(HERE/'model_test/completion.json')['complete'];out=HERE/'application_test';out.mkdir(exist_ok=True)
 for i,c in enumerate(d['cases']):
  ref=HERE/'references'/(c['id']+'.json.gz');check=HERE/'references'/(c['id']+'_check.json.gz')
  if not check.exists() or not rt.read(check)['success']:
   write(out/(c['id']+'_excluded.json'),dict(case=c['id'],reason='Main reference check did not complete.'));continue
  with tempfile.TemporaryDirectory(prefix='learned_seed_cli_',dir=os.environ['TMPDIR']) as tmp:
   tmp=Path(tmp);case_path=tmp/'case.json';basis_path=tmp/'basis.json';result=tmp/'result.json.gz';write(case_path,c);write(basis_path,rt.read(ref)['masters'])
   for repeat in range(d['repetitions']):
    methods=d['methods'];k=(i+repeat)%len(methods);methods=methods[k:]+methods[:k]
    for m in methods:
     p=out/(c['id']+'_'+m+f'_r{repeat}.json.gz')
     if p.exists():continue
     if result.exists():result.unlink()
     cmd=[sys.executable,str(HERE/'s10_secondary.py'),'--child',str(case_path),str(basis_path),str(result)] if m=='previous' else [sys.executable,str(HERE/'s01_runtime.py'),'--case',str(case_path),'--basis',str(basis_path),'--output',str(result),'--method',m]
     tick=time.perf_counter()
     with rt.environment():z=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=600)
     process_seconds=time.perf_counter()-tick
     r=rt.read(result) if result.exists() else dict(success=False,coefficients={},attempts=[])
     r.update(case=c['id'],method=m,repeat=repeat,process_seconds=process_seconds,process_returncode=z.returncode,process_log_tail=z.stdout[-1200:])
     rt.verify(r,ref);r['complete_seconds']=time.perf_counter()-tick;rt.save(p,r)
     print(json.dumps(dict(stage='fresh_application',case=c['id'],method=m,repeat=repeat,seconds=r['complete_seconds'],success=r['success'])),flush=True)
 matched=[];failed=[];requests=[]
 for c in d['cases']:
  runs={m:[rt.read(p) for j in range(d['repetitions']) if (p:=out/(c['id']+'_'+m+f'_r{j}.json.gz')).exists()] for m in d['methods']};requests.extend(r for v in runs.values() for r in v)
  if not all(len(v)==d['repetitions'] and all(r['success'] for r in v) for v in runs.values()):failed.append(c['id']);continue
  coeff=runs['native'][0]['coefficients']
  if all(v=={t:'1'} for t,v in coeff.items()):continue
  matched.append(dict(case=c['id'],graph=c['topology_group'],seconds={m:statistics.median(r['complete_seconds'] for r in v) for m,v in runs.items()}))
 totals={m:sum(c['seconds'][m] for c in matched) for m in d['methods']}
 write(out/'summary.json',dict(complete=True,cases=matched,totals=totals,ratios={m:totals['learned']/totals[m] if totals[m] else None for m in ['native','previous']},failed=failed,timed=len(requests),successful=sum(r['success'] for r in requests),protocol_sha256=sha(HERE/'application_protocol.json')))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--child',nargs=3);a=p.parse_args()
 if a.child:child(*a.child)
 elif a.freeze:plan()
 else:main()
