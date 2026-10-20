"""Collect complete native costs for three exact seed policies."""
from s00_light_common import *
from s05_runtime import ACTIONS,features
from s06_native_cases import native_cases
from s07_measure import measured

def main(worker):
 assert read(HERE/'checks.json')['complete']
 vac=previous().previous();h=vac.batch.legacy().h;measure=load('lightlike_native_reference',vac.BATCH/'s04_measure.py')
 for phase in ['training','validation']:
  for i,c in enumerate(native_cases(phase)):
   if i%2!=worker:continue
   dest=HERE/phase/(c['id']+'.json.gz')
   if dest.exists():continue
   ref=measure.reference(c);rows={a:[] for a in ACTIONS}
   for rep in range(1 if phase=='training' else 2):
    order=ACTIONS[(i+rep)%3:]+ACTIONS[:(i+rep)%3]
    for a in order:
     r,t=measured(c,a,worker);ok,n=h.compare(r,ref) if r.get('success') and ref.get('success') else (False,0)
     rows[a].append(dict(result=r,application_seconds=t,verified=ok,checks=n))
   write(dest,dict(case=c,features=features(c),reference=ref,measurements=rows));print(json.dumps(dict(phase=phase,case=c['id'],times={a:[round(x['application_seconds'],3) for x in rr] for a,rr in rows.items()},verified={a:all(x['verified'] for x in rr) for a,rr in rows.items()})),flush=True)
 write(HERE/f'collection{worker}.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
