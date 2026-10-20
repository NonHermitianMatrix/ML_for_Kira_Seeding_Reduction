"""Compare all completed requests with one or separate application processes."""
from s00_reconstruction_common import *
from s06_measure import measured
import signal,shutil,socket

def batch(cases,limit,worker,method):
 request=HERE/'requests'/f'batch_cases{worker}.json'
 out=HERE/'requests'/f'batch_results{worker}.jsonl'
 write(request,cases);out.unlink(missing_ok=True)
 start=time.perf_counter()
 p=subprocess.Popen([sys.executable,str(HERE/'s37_batch.py'),'--cases',str(request),'--output',str(out),'--method',method],
  stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
 timed_out=False
 try:_,err=p.communicate(timeout=limit)
 except subprocess.TimeoutExpired:
  timed_out=True;h=helper()
  limits=h.inputs.module('batch_limits',h.BLOCK/'s11_extension_test.py')
  pids=limits.descendants(p.pid)
  for pid in pids:
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  _,err=p.communicate()
  for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ.get('TMPDIR','/tmp'))]:
   for pid in pids:
    for q in root.glob(f'ml_kira_{pid}_*'):
     if q.is_dir():shutil.rmtree(q)
 elapsed=time.perf_counter()-start
 rows={}
 if out.exists():
  assert out.stat().st_size<8*1024**2
  for line in out.read_text().splitlines():
   try:r=json.loads(line)
   except json.JSONDecodeError:
    assert timed_out;continue
   assert r['case'] not in rows;rows[r['case']]=r
 for c in cases:
  if c['id'] not in rows:
   rows[c['id']]=dict(case=c['id'],seconds=None,result=dict(success=False,status='batch_deadline' if timed_out else 'missing_batch_output'))
 request.unlink(missing_ok=True);out.unlink(missing_ok=True)
 return rows,elapsed,dict(timed_out=timed_out,returncode=p.returncode,stderr_tail=err.decode(errors='replace')[-1200:])

def main(worker):
 protocol=read(HERE/'batch_protocol.json.gz')
 assert all(sha(HERE/n)==h for n,h in protocol['source_sha256'].items())
 assert all(sha(HERE/'trained_model'/n)==h for n,h in protocol['model_sha256'].items())
 assert sha(TOOLS/'kira')==protocol['binary_sha256']
 direct=load('batch_exact_check',PREVIOUS/'s27_deploy_test.py')
 for rep in range(protocol['repetitions']):
  if rep%2!=worker:continue
  # Reverse the full request order to check that retained state does not alter answers.
  cases=protocol['cases'][::(-1 if rep%2 else 1)]
  for method in protocol['methods'][::(-1 if rep%2 else 1)]:
   dest=HERE/'batch_test'/f'{rep}_{method}.json.gz'
   if dest.exists():continue
   application='before_formulas' if method.startswith('earlier_') else 'integrated'
   if method.endswith('batch'):rows,elapsed,process=batch(cases,protocol['seconds_per_batch'],worker,application)
   else:
    rows={};elapsed=0;process=dict(timed_out=False)
    for c in cases:
     r,t=measured(c,application,worker,protocol['seconds_per_separate_application'],entry='s15_deploy.py')
     elapsed+=t;rows[c['id']]=dict(case=c['id'],seconds=t,result=r)
   checks=0;failed=[]
   for c in cases:
    refpath=HERE/'test_references'/(c['id']+'.json.gz')
    assert sha(refpath)==protocol['reference_sha256'][c['id']]
    ok,n=direct.compare(c,rows[c['id']]['result'],read(refpath))
    rows[c['id']].update(verified=ok,coefficient_checks=n);checks+=n
    if not ok:failed.append(c['id'])
   write(dest,dict(method=method,repetition=rep,total_seconds=elapsed,
    results=rows,checks=checks,failed=failed,process=process,
    host=socket.gethostname(),order=[c['id'] for c in cases]))
   print(rep,method,elapsed,'failures',len(failed),'checks',checks,flush=True)
   if failed:raise AssertionError(failed)
 write(HERE/f'batch{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'batch_protocol.json.gz')))

if __name__=='__main__':main(int(sys.argv[1]))
