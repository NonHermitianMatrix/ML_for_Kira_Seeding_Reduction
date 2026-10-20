"""Compare the frozen exact extension, its fixed control, and the prior application."""
from s00_tensor_common import *
from s06_measure import measured
from s01_tensor import reduce

def reference(c):
 old=previous();h=old.batch.legacy().h
 if c['test_group'] in ['tensor','other_masses','products']:
  blocks=[]
  for part in old.batch.support.split_blocks(c):
   r=reduce(part['case'],'powers_smallest',deadline=time.perf_counter()+20)
   if r is None:r=reduce(part['case'],'tensor_largest',deadline=time.perf_counter()+20)
   assert r is not None,(c['id'],'reference exact recurrence limit')
   blocks.append(dict(case=part['case'],indices=part['indices'],result=r))
  return dict(success=True,blocks=blocks)
 if c['test_group']=='native':
  m=load('tensor_native_test_reference',old.BATCH/'s04_measure.py');return m.reference(c)
 return old.run(c,'all_fixed')

def compare(c,result,ref,h):
 ok,n=h.compare(result,ref)
 if ok or c['test_group'] not in ['tensor','other_masses','products']:return ok,n
 import sympy as sp
 references={tuple(b['indices']):b for b in ref['blocks']};checks=0
 if len(result.get('blocks',[]))!=len(references):return False,0
 for block in result['blocks']:
  expected=references.get(tuple(block['indices']))
  if expected is None:return False,0
  rows=block['result']['coefficients'];cc=copy.deepcopy(block['case']);masters=list(dict.fromkeys(tuple(map(int,m.split(','))) for row in rows.values() for m in row));cc['targets']=[list(m) for m in masters]+cc['targets'];basis=reduce(cc,'tensor_largest',deadline=time.perf_counter()+20)
  if basis is None:return False,0
  converted={}
  for target,row in rows.items():
   out={}
   for m,v in row.items():
    for k,w in basis['coefficients'][m].items():out[k]=out.get(k,0)+sp.sympify(v)*sp.sympify(w)
   converted[target]={k:str(sp.cancel(v)) for k,v in out.items() if sp.cancel(v)!=0}
  ok,n=h.equal(converted,expected['result']['coefficients'])
  if not ok:return False,checks
  checks+=n
 return True,checks

def main(worker):
 p=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];h=previous().batch.legacy().h
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'model_test'/(c['id']+'.json.gz')
  if dest.exists():continue
  methods=['integrated','all_fixed','previous'];times={m:[] for m in methods};statuses={m:[] for m in methods};success={m:[] for m in methods};checks=0;saved={}
  ref=reference(c);assert ref.get('success'),(c['id'],'independent or recurrence reference failed',ref)
  for rep in range(p['repetitions']):
   order=methods[(i+rep)%len(methods):]+methods[:(i+rep)%len(methods)]
   for method in order:
    r,t=measured(c,method,worker,p['seconds_per_application']);ok=False;n=0
    if r.get('success'):
     ok,n=compare(c,r,ref,h);assert ok,(c['id'],method,'exact coefficient disagreement')
    checks+=n;times[method].append(t);success[method].append(ok);statuses[method].append(r.get('status'));saved[method]=r
  row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),targets=c['size'],coordinates=len(c['definition']['propagators']),physical=c['definition']['physical_propagators'],times=times,median_seconds={m:statistics.median(v) for m,v in times.items()},statuses=statuses,success=success,checks=checks,results=saved)
  write(dest,row);print(json.dumps({k:v for k,v in row.items() if k in ['case','median_seconds','statuses','success']}),flush=True)
 write(HERE/f'test{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
