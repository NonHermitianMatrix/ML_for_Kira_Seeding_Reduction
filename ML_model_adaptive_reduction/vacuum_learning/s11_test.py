"""Measure frozen native and exact choices on reserved inputs."""
from s00_vac_common import *
from s01_vacuum import reduce
from s05_measure import measured,reference
from s09_checks import gamma_check
import sympy as sp

def check_vac(c,r,ref):
 if not r.get('success'):return False,0
 rows=r['blocks'][0]['result'];cc=copy.deepcopy(c);cc['targets']=rows['masters'];mr=reduce(cc)
 if mr is None:return False,0
 n=0
 for target,row in rows['coefficients'].items():
  got=sum(sp.sympify(v)*sp.sympify(next(iter(mr['coefficients'][k].values()))) for k,v in row.items())
  expected=sp.sympify(next(iter(ref['coefficients'][target].values())))
  assert sp.cancel(got-expected)==0,(c['id'],target);n+=1
 return n==len(c['targets']),n

def main(worker):
 p=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];h=batch.legacy().h
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'results'/(c['id']+'.json.gz')
  if dest.exists():continue
  methods=['integrated','previous']+(['all_fixed'] if c['test_group']=='native' else [])
  times={m:[] for m in methods};statuses={m:[] for m in methods};success={m:[] for m in methods};checks=0;saved={};ref=None;gamma=dict(passed=True,checks=0)
  if c['test_group']=='vacuum':ref=reduce(c);gamma=gamma_check(c,ref)
  elif c['test_group']=='native':ref=reference(c)
  for rep in range(p['repetitions']):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    r,seconds=measured(c,method,worker,p['seconds_per_application']);ok=False;n=0
    if r.get('success'):
     if c['test_group']=='vacuum':ok,n=check_vac(c,r,ref)
     else:
      if ref is None:ref=r
      ok,n=h.compare(r,ref) if ref.get('success') else (False,0)
     if ref.get('success',True):assert ok,(c['id'],method,'exact comparison failed')
    times[method].append(seconds);statuses[method].append(r.get('status'));success[method].append(ok);checks+=n;saved[method]=r
  row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),shape=c.get('shape'),targets=c['size'],times=times,median_seconds={m:statistics.median(v) for m,v in times.items()},statuses=statuses,success=success,checks=checks,gamma=gamma,results=saved)
  write(dest,row);print(json.dumps({k:v for k,v in row.items() if k in ['case','median_seconds','statuses','success']}),flush=True)
 write(HERE/f'test{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
