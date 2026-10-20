"""Measure all eight native integral orderings on development inputs only."""
from s00_direct_common import *
from s03_cases import cases
from s02_measure import measured
worker=int(sys.argv[1]);h=helper()
for c in cases('development')[worker::2]:
 ref=reference_module().reference(c);write(HERE/'references'/(c['id']+'.json.gz'),ref)
 assert ref['success'],c['id']
 for order in range(1,9):
  dest=HERE/'development'/(c['id']+'_order'+str(order)+'.json.gz')
  if dest.exists():continue
  r,elapsed=measured(c,'order'+str(order),worker,30);ok,n=h.compare(r,ref) if r.get('success') else (False,0)
  r.update(case=c['id'],application_seconds=elapsed,verified=ok,coefficient_checks=n,order=order);write(dest,r);print(c['id'],order,round(elapsed,3),ok,flush=True)
write(HERE/f'pilot{worker}.json',dict(complete=True))
