"""Measure complete native actions for disjoint training and validation batches."""
from s00_direct_common import *
from s03_cases import cases
from s02_measure import measured

def main(worker):
 actions=read(HERE/'actions.json')['actions'];h=helper();rows=[(phase,c) for phase in ['training','validation'] for c in cases(phase)]
 for i,(phase,c) in enumerate(rows):
  if i%2!=worker:continue
  dest=HERE/phase/(c['id']+'.json.gz')
  if dest.exists():continue
  ref=reference_module().reference(c);assert ref['success'],c['id'];ms={a:[] for a in actions}
  for rep in range(2):
   order=actions[(i+rep)%3:]+actions[:(i+rep)%3]
   for action in order:
    r,elapsed=measured(c,action,worker,30);ok,n=h.compare(r,ref) if r.get('success') else (False,0)
    if r.get('success'):assert ok,(c['id'],action,'coefficient disagreement')
    attempts=[a for b in r.get('blocks',[]) for a in b['result'].get('attempts',[])];ms[action].append(dict(application_seconds=elapsed,verified=ok,coefficient_checks=n,status=r.get('status'),failed_attempts=sum(not a.get('success',False) for a in attempts),first_attempt_failed=bool(attempts) and not attempts[0].get('success',False)))
  write(dest,dict(case=c,features=current().features(c),measurements=ms,reference=ref));print(c['id'],{a:round(statistics.median(r['application_seconds'] for r in ms[a]),3) for a in actions},flush=True)
 write(HERE/f'collection{worker}.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
