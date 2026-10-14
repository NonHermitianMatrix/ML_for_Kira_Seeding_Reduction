"""Test frozen choices on reserved profiles, including independent exact checks."""
import json,time,resource
import s05_fit as model
w=model.w
METHODS=['native','previous','previous_four','family_fixed','selected']
def application(c,basis,f):
 start=time.perf_counter();cfg,reason=model.select(f,c)
 decision_seconds=time.perf_counter()-start
 r=w.workflow(c,basis,cfg)
 r['worker_prediction_seconds']=decision_seconds
 r.update(selection_reason=reason,reference_coefficients_supplied=False,complete_seconds=time.perf_counter()-start)
 return r
def main():
 protocol=json.loads((w.HERE/'protocol.json').read_text());f=json.loads((w.HERE/'trained_model/freeze.json').read_text());model.check_freeze(f)
 for ci,c in enumerate(c for c in protocol['cases'] if c['split']=='reserved'):
  ref=w.reference(c);basis=w.read(ref)['masters']
  for rep in range(5):
   offset=(ci+rep)%len(METHODS);order=METHODS[offset:]+METHODS[:offset]
   for method in order:
    p=w.HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
    if p.exists():continue
    start=time.perf_counter();cpu0=sum(resource.getrusage(who).ru_utime+resource.getrusage(who).ru_stime for who in [resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN])
    if method=='native':
     r=w.st.workflow(c,None,'native',basis);r['coefficients']=r['attempts'][-1].get('coefficients',{});w.verify(c,r,basis,ref)
    else:
     if method=='selected':cfg,reason=model.select(f,c)
     elif method=='previous_four':cfg='threads4';reason=method
     else:cfg='previous' if method=='previous' else f['policies'][c['topology_group']]['best_fixed'];reason=method
     decision_seconds=time.perf_counter()-start
     r=w.workflow(c,basis,cfg,ref);r['selection_reason']=reason
     r['worker_prediction_seconds']=decision_seconds
    cpu1=sum(resource.getrusage(who).ru_utime+resource.getrusage(who).ru_stime for who in [resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN])
    r.update(method=method,repetition=rep,complete_seconds=time.perf_counter()-start,cpu_seconds=cpu1-cpu0)
    w.save(p,r);w.emit(stage='test',case=c['id'],method=method,success=r['success'],seconds=r['complete_seconds'],fallback=r['fallback_count'])
    assert r['success'] and r['reference_checked']
  p=w.HERE/'model_test'/f'{c["id"]}_application.json.gz'
  if not p.exists():
   r=application(c,basis,f);duration=r['complete_seconds'];w.verify(c,r,basis,ref)
   r.update(independent_exact_checks=r['coefficient_checks'],application_seconds=duration,all_exact=r['success'])
   w.save(p,r);assert r['success']
 w.emit(stage='tests_complete')
if __name__=='__main__':main()
