"""Frozen comparison of complete decomposition time and exact coefficients."""
from s00_light_common import *
from s07_measure import measured
from s05_runtime import independent_parts
from s01_lightlike import reduce as lightlike
from s12_complete_tensor import reduce as tensor
from s09_symbolic import reduce as symbolic

def canonical_rows(c,rows):
 import sympy as sp
 masses=[sp.sympify(p['mass_squared']) for p in c['definition']['propagators']];out={}
 for t,row in rows.items():
  rr={}
  for m,v in row.items():
   a=list(map(int,m.split(',')))
   if sum(a)==1 and a.count(1)==1:
    mass=masses[a.index(1)]
    if mass==0:continue
    z=[0]*len(a);z[next(i for i,x in enumerate(masses) if sp.cancel(x-mass)==0)]=1;m=label(z)
   rr[m]=rr.get(m,0)+sp.sympify(v)
  out[t]={m:str(sp.cancel(v)) for m,v in rr.items() if sp.cancel(v)!=0}
 return out

def reference(c):
 vac=previous().previous();h=vac.batch.legacy().h;measure=load('lightlike_reserved_reference',vac.BATCH/'s04_measure.py')
 if c['test_group']=='native':return measure.reference(c)
 if c['test_group']=='vacuum':return previous().run(c,'all_fixed')
 blocks=[];memo={}
 for p in independent_parts(c) or [dict(case=c,indices=list(range(len(c['definition']['propagators']))))]:
  cc=p['case'];key=json.dumps([cc['definition'],cc['targets']],sort_keys=True)
  if key not in memo:
   # Native IBP supplies the independent reference, including symbolic masses.
   memo[key]=measure.native(h,cc,None,expanded=True)
  r=memo[key];blocks.append(dict(case=cc,indices=p['indices'],result=r))
  if not r.get('success'):break
 return dict(success=all(b['result'].get('success') for b in blocks),blocks=blocks)

def compare(c,r,ref):
 h=previous().previous().batch.legacy().h
 if c['test_group'] in ['native','vacuum']:return h.compare(r,ref)
 refs={tuple(b['indices']):b for b in ref['blocks']};n=0
 if len(r.get('blocks',[]))!=len(refs):return False,0
 for block in r['blocks']:
  other=refs.get(tuple(block['indices']))
  if other is None:return False,n
  ok,k=h.equal(canonical_rows(block['case'],block['result']['coefficients']),canonical_rows(other['case'],other['result']['coefficients']))
  if not ok:return False,n
  n+=k
 return True,n

def main(worker):
 p=read(HERE/'protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['source_sha256'].items());assert sha(HERE/'trained_model/policy.json')==p['model_sha256']
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'model_test'/(c['id']+'.json.gz')
  if dest.exists():continue
  ref=reference(c);methods=['integrated','all_fixed','previous'];times={m:[] for m in methods};success={m:[] for m in methods};statuses={m:[] for m in methods};saved={};checks=0
  for rep in range(p['repetitions']):
   order=methods[(i+rep)%3:]+methods[:(i+rep)%3]
   for method in order:
    r,t=measured(c,method,worker,p['seconds_per_application']);ok=False;n=0
    if ref.get('success') and r.get('success'):
     ok,n=compare(c,r,ref);assert ok,(c['id'],method,'coefficient disagreement')
    times[method].append(t);success[method].append(ok);statuses[method].append(r.get('status'));saved[method]=r;checks+=n
  row=dict(case=c['id'],group=c['test_group'],loops=len(c['definition']['loop_momenta']),targets=c['size'],reference_success=ref.get('success'),reference=ref,times=times,success=success,statuses=statuses,median_seconds={m:statistics.median(v) for m,v in times.items()},checks=checks,results=saved)
  write(dest,row);print(json.dumps({k:v for k,v in row.items() if k in ['case','group','reference_success','median_seconds','success','statuses']}),flush=True)
 write(HERE/f'test{worker}.json',dict(complete=True,protocol_sha256=sha(HERE/'protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
