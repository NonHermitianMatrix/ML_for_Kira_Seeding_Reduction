"""Check new master-index sets separately from learned target decisions."""
from s00_batch_common import *
from s03_cases import batches,triangle
from s04_measure import native

def main():
 for w in [0,1]:assert read(HERE/f'development_{w}_complete.json')['complete']
 h=legacy().h;records=[];registry={};start=time.perf_counter()
 cases=[batches(3001,'development')[i] for i in [0,3,6]]+[triangle(3001),triangle(3001,symbolic=True)]
 for c in cases:
  ref=read(HERE/'references'/(c['id']+'.json.gz'));assert ref['success'];bs=ref['blocks'][0]['result']['masters']
  a=native(h,c,bs,ordering=1,expanded=False);b=native(h,c,bs,ordering=2,expanded=False)
  ok,n=h.equal(a.get('coefficients',{}),b.get('coefficients',{})) if a['success'] and b['success'] else (False,0)
  if ok:ok,n2=h.equal(a['coefficients'],ref['blocks'][0]['result']['coefficients']);n+=n2
  record=dict(case=c,verified=ok,coefficient_checks=n,first=a,second=b,reference_sha256=sha(HERE/'references'/(c['id']+'.json.gz')))
  write(HERE/'basis_checks'/(c['id']+'.json.gz'),record);assert ok,c['id']
  k=h.old.key(c);stored=h.old.store_basis(c,bs)
  if k in registry:assert set(map(tuple,stored))==set(map(tuple,registry[k]['basis']))
  registry[k]=dict(basis=stored,source='Separate native reductions with two integral orderings and exact coefficient agreement. Indices only; no reduction coefficients.')
  records.append(dict(case=c['id'],checks=n,masters=len(bs)));print(json.dumps(records[-1]),flush=True)
 write(HERE/'basis_registry.json',registry);write(HERE/'basis_validation.json',dict(complete=True,cases=records,preparation_seconds=time.perf_counter()-start,basis_sha256=sha(HERE/'basis_registry.json')))
if __name__=='__main__':main()
