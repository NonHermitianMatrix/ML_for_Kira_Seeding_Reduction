"""Measure disjoint training and validation batches with exact native references."""
from s00_vac_common import *
from s04_cases import native_cases
from s05_measure import measured,reference

def main(worker):
 h=batch.legacy().h
 for phase in ['training','validation']:
  cases=native_cases(phase);reps=1 if phase=='training' else 2
  for i,c in enumerate(cases):
   if i%2!=worker:continue
   path=HERE/phase/(c['id']+'.json.gz')
   if path.exists():continue
   ref=reference(c);rows={a:[] for a in ACTIONS}
   for rep in range(reps):
    order=ACTIONS[(i+rep)%3:]+ACTIONS[:(i+rep)%3]
    for a in order:
     r,seconds=measured(c,a,worker);tick=time.perf_counter();ok,n=h.compare(r,ref) if ref.get('success') and r.get('success') else (False,0)
     rows[a].append(dict(result=r,application_seconds=seconds,check_seconds=time.perf_counter()-tick,verified=ok,checks=n))
   write(path,dict(case=c,features=features(c),reference_success=ref.get('success'),measurements=rows))
   print(json.dumps(dict(phase=phase,case=c['id'],costs={a:[round(x['application_seconds'],3) for x in rs] for a,rs in rows.items()},verified={a:all(x['verified'] for x in rs) for a,rs in rows.items()})),flush=True)
 write(HERE/f'collection{worker}_complete.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
