"""Measure four exact order choices on separate training and validation families."""
from s00_tensor_common import *
from s03_cases import cases
from s19_fast_measure import measured

def main(worker):
 h=previous().batch.legacy().h
 for phase in ['training','validation']:
  for i,c in enumerate(cases(phase)):
   if i%2!=worker:continue
   path=HERE/('fast_'+phase)/(c['id']+'.json.gz')
   if path.exists():continue
   original=read(HERE/phase/(c['id']+'.json.gz'));rows={a:[] for a in ACTIONS};reference=original['reference'];reference_method='original_symbolic_field'
   for rep in range(1 if phase=='training' else 2):
    order=ACTIONS[(i+rep)%4:]+ACTIONS[:(i+rep)%4]
    for a in order:
     r,seconds=measured(c,a,worker);ok=False;n=0
     if r.get('success'):
      assert r['blocks'][0]['result']['route']=='exact_one_loop_tensor',(c['id'],a,'exact domain failed')
      if reference is None:reference=r;reference_method=a
      ok,n=h.compare(r,reference);assert ok,(c['id'],a,'coefficient disagreement')
     rows[a].append(dict(application_seconds=seconds,verified=ok,checks=n,status=r.get('status'),states=[b['result'].get('recurrence_states') for b in r.get('blocks',[])],route=[b['result'].get('route') for b in r.get('blocks',[])]))
   write(path,dict(case=c,features=features(c),reference_method=reference_method,reference=reference,measurements=rows))
   print(json.dumps(dict(phase=phase,case=c['id'],costs={a:[round(x['application_seconds'],3) for x in rs] for a,rs in rows.items()},verified={a:all(x['verified'] for x in rs) for a,rs in rows.items()})),flush=True)
 write(HERE/f'fast_collection{worker}_complete.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
