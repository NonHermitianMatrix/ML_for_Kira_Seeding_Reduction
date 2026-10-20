"""Check a frozen learned equation filter with fixed reconstruction settings."""
from s00_triangle_common import *
from s02_triangle_cases import native_cases
from s04_triangle_measure import compare
from s27_equation_runtime import WEIGHTS
import statistics,signal,random,shutil

def measure(c,mode):
 src=HERE/'requests/eq_input.json';out=HERE/'requests/eq_output.json.gz';write(src,c);out.unlink(missing_ok=True);start=time.perf_counter()
 p=subprocess.Popen([sys.executable,str(HERE/'s27_equation_runtime.py'),'--case',str(src),'--output',str(out),'--mode',mode],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,start_new_session=True)
 try:
  _,err=p.communicate(timeout=90);r=read(out) if out.exists() else dict(success=False,status='missing_output');r['stderr_tail']=err.decode(errors='replace')[-1200:]
 except subprocess.TimeoutExpired:
  h=helper();lim=h.inputs.module('triangle_eq_limits',h.BLOCK/'s11_extension_test.py');pids=lim.descendants(p.pid)
  for pid in pids:
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  p.communicate();r=dict(success=False,status='application_deadline')
  for root in [ROOT/'.tools/kira-integrated-runtime',Path(os.environ.get('TMPDIR','/tmp'))]:
   for pid in pids:
    for q in root.glob(f'ml_kira_{pid}_*'):
     if q.is_dir():shutil.rmtree(q)
 src.unlink(missing_ok=True);out.unlink(missing_ok=True);return r,time.perf_counter()-start

def main(phase):
 assert os.environ.get('JOB_ID') and phase in ['validation','reserved'];cases=[c for c in native_cases(phase) if c['topology_group']=='nonplanar_box'];out=[]
 protocol=dict(phase=phase,weights_sha256=sha(WEIGHTS),threshold=.05,repetitions=2 if phase=='validation' else 3,cases=cases,source_sha256={n:sha(HERE/n) for n in ['s27_equation_runtime.py','s28_equation_compare.py','s30_monitor.py']},base_protocol_sha256=sha(HERE/'test_protocol.json.gz'))
 write(HERE/('equation_'+phase+'_protocol.json.gz'),protocol)
 for c in cases:
  ref=read(HERE/('symbolic_references' if phase=='validation' else 'test_references')/(c['id']+'.json.gz'))
  if phase=='validation':ref=ref['result']
  row=dict(case=c['id'],times={},results={},checks=0,verified=True)
  for rep in range(protocol['repetitions']):
   modes=['off','on'];random.Random(c['id']+str(rep)).shuffle(modes)
   for mode in modes:
    r,t=measure(c,mode);ok,n=compare(c,r,ref) if r.get('success') else (False,0);row['times'].setdefault(mode,[]).append(t);row['results'].setdefault(mode,[]).append(r);row['checks']+=n;row['verified'] &=ok
    write(HERE/('equation_'+phase)/(c['id']+'.json.gz'),row)
  out.append(row);print(phase,c['id'],{a:statistics.median(v) for a,v in row['times'].items()},row['verified'],flush=True)
 sums={a:sum(statistics.median(r['times'][a]) for r in out) for a in ['off','on']};retried=sum(r.get('equation_filter_extension',{}).get('disabled_after_failure',False) for row in out for r in row['results']['on']);attempts=sum(r.get('equation_filter_extension',{}).get('attempts',0) for row in out for r in row['results']['on'])
 summary=dict(complete=True,phase=phase,seconds=sums,ratio=sums['on']/sums['off'],all_verified=all(r['verified'] for r in out),checks=sum(r['checks'] for r in out),filter_attempts=attempts,filter_retries=retried,protocol_sha256=sha(HERE/('equation_'+phase+'_protocol.json.gz')))
 summary['admitted']=summary['all_verified'] and not retried and attempts>0 and summary['ratio']<.97
 write(HERE/('equation_'+phase+'_summary.json'),summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main(sys.argv[1])
