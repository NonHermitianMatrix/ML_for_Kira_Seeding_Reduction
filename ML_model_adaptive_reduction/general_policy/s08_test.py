"""Fresh-process held-out tests, including all requested loop orders 1--12."""
from s00_common import *
import subprocess
PYTHON=ROOT/'.tools/seed-model/venv/bin/python'
B=HERE/'refit'
def call(c,m,p,basis=None,reference=None):
 if p.exists():return READ(p)
 q=B/'requests'/(p.stem+'.json');write(q,dict(case=c,method=m,basis=basis,reference=str(reference) if reference else None))
 temp=p.with_name(p.name+'.pending.gz');p.parent.mkdir(parents=True,exist_ok=True)
 begin=time.perf_counter()
 try:
  worker=HERE/'s07_application.py'
  if m=='previous':worker=ROOT/'ML_model_adaptive_reduction/portfolio_policy/s13_optimized.py'
  if m=='previous':write(q,dict(case=c,method='optimized_application',basis=basis,reference=str(reference) if reference else None))
  proc=subprocess.run([str(PYTHON),str(worker),'--input',str(q),'--output',str(temp)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=240)
  result=READ(temp) if temp.exists() else dict(success=False,status='worker_exit',error=proc.stderr.decode()[-1500:])
 except subprocess.TimeoutExpired:result=dict(success=False,status='outer_time_limit')
 result.update(complete_seconds=time.perf_counter()-begin,method=m,case=c['id'],process_timer_complete=True)
 write(p,result);q.unlink()
 if temp.exists():temp.unlink()
 print(c['id'],m,result['success'],round(result['complete_seconds'],3),flush=True);return result

def main(worker):
 protocol=READ(B/'protocol.json');freeze=READ(B/'trained_model/freeze.json');assert freeze['complete']
 fhash=inputs.sha(B/'trained_model/freeze.json')
 for c in protocol['reserved'][worker::2]:
  output=B/'coverage'/(c['id']+'.json')
  if output.exists():continue
  loops=len(c['definition']['loop_momenta']);n=len(c['definition']['propagators'])
  info=dict(case=c['id'],loops=loops,indices=n,physical_holdout=held_out(c),shape=c['shape'])
  if n>31:
   # Evaluate the dimension-independent model, but do not claim a native reduction.
   from s02_application import predict
   scores=predict(freeze['model'],features(c));write(output,info|dict(status='unsupported_native_index_count',predicted_action=ACTIONS[min(range(len(ACTIONS)),key=scores.__getitem__)]));continue
  ref=B/'references'/(c['id']+'.json.gz');r=call(c,'reference',ref)
  if not r['success']:write(output,info|dict(status='reference_failed',reason=r.get('status')));continue
  basis=r['masters'];check=call(c,'check',B/'references'/(c['id']+'_check.json.gz'),basis,ref)
  if not check['success']:write(output,info|dict(status='independent_check_failed',reason=check.get('status')));continue
  methods=['native','fixed','learned','previous'];failed=set()
  for rep in range(protocol['repetitions']):
   shift=(sum(c['id'].encode())+rep)%len(methods)
   for m in methods[shift:]+methods[:shift]:
    if m in failed:continue
    out=call(c,m,B/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz'),basis,ref)
    if not out['success']:failed.add(m)
  write(output,info|dict(status='verified' if not failed else 'method_failed',failed_methods=sorted(failed),masters=len(basis)))
 assert inputs.sha(B/'trained_model/freeze.json')==fhash
 write(B/('test_'+str(worker)+'_complete.json'),dict(complete=True,model_sha256=fhash))
if __name__=='__main__':main(int(sys.argv[1]))
