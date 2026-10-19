"""Test the output change with unchanged algebra and frozen model weights."""
from s00_vac_common import *
from s05_measure import reference
import subprocess,signal,shutil

def measured(c,method,worker,limit):
 request=HERE/'requests'/f'output_case{worker}.json';old=method=='previous'
 dest=(PRIOR if old else HERE)/'requests'/f'output_result{worker}.json.gz';write(request,c)
 script=PRIOR/'s02_runtime.py' if old else HERE/('s03_runtime.py' if method=='first' else 's18_fast_runtime.py')
 setting='all_fixed' if method=='fast_fixed' else 'integrated';start=time.perf_counter()
 proc=subprocess.Popen([sys.executable,str(script),'--case',str(request),'--output',str(dest),'--method',setting],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=proc.communicate(timeout=limit);r=read(dest) if dest.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-500:]
 except subprocess.TimeoutExpired:
  h=batch.legacy().h;helper=h.inputs.module('vac_fast_process_limits',h.BLOCK/'s11_extension_test.py');pids=helper.descendants(proc.pid)
  for pid in pids:
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  proc.communicate();r=dict(success=False,status='application_deadline')
  for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ['TMPDIR'])]:
   for pid in pids:
    for scratch in root.glob(f'ml_kira_{pid}_*'):
     if scratch.is_dir():shutil.rmtree(scratch)
 finally:request.unlink(missing_ok=True);dest.unlink(missing_ok=True)
 return r,time.perf_counter()-start

def main(worker):
 p=read(HERE/'output_protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];h=batch.legacy().h
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  path=HERE/'output_test'/(c['id']+'.json.gz')
  if path.exists():continue
  methods=['fast','first']+(['fast_fixed'] if c['test_group']=='native' else ['previous'] if c['test_group'] in ['propagator','triangle'] else [])
  ref=reference(c) if c['test_group']=='native' else None
  times={m:[] for m in methods};success={m:[] for m in methods};statuses={m:[] for m in methods};checks=0;saved={}
  for rep in range(p['repetitions']):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    r,t=measured(c,method,worker,p['seconds_per_application']);ok=False;n=0
    if r.get('success'):
     if ref is None:ref=r
     ok,n=h.compare(r,ref) if ref.get('success') else (False,0)
     assert ok,(c['id'],method,'exact coefficient mismatch')
    checks+=n;times[method].append(t);success[method].append(ok);statuses[method].append(r.get('status'));saved[method]=r
  row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),targets=c['size'],times=times,median_seconds={m:statistics.median(v) for m,v in times.items()},success=success,statuses=statuses,checks=checks,results=saved)
  write(path,row);print(json.dumps({k:v for k,v in row.items() if k in ['case','median_seconds','success']}),flush=True)
 write(HERE/f'output_test{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'output_protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
