"""Measure complete partition costs on development or training inputs only."""
import argparse,json,time
from s00_runtime import HERE,ACTIONS,rt,inputs,save,run,partition
from s01_cases import initialize,make,reference

def collect(stage):
 initialize();h={'development':701,'training':711,'validation':712,'validation_off':712}[stage]
 cases=make(h,stage,graphs=['double_box','ladder3','nonplanar_box'] if stage=='development' else None) if stage=='development' else make(h,stage)
 if stage=='development':cases=[c for c in cases if c['shape'] in ['dots','dots_rank','all']]
 reps=1 if stage=='development' else 2 if stage=='training' else 3
 canonical={}
 for c in cases:
  seen={};mapping={}
  for a in ACTIONS:
   key=(stage!='validation_off' and a!='whole_off',tuple(tuple(map(tuple,q['targets'])) for q in partition(c,a)))
   mapping[a]=seen.setdefault(key,a)
  canonical[c['id']]=mapping
 p=HERE/stage/'protocol.json';protocol=dict(cases=cases,actions=ACTIONS,repetitions=reps,profile=h,canonical_partitions=canonical,equivalent_costs='Identical ordered target parts share one measured cost; no repeated timing is claimed for aliases.')
 if p.exists():assert rt.read(p)==protocol
 else:inputs.write(p,protocol)
 for ci,c in enumerate(cases):
  ref=reference(c)
  if ref is None:print('REFERENCE_FAILED',c['id'],flush=True);continue
  for j in range(reps):
   for k in [(n+ci+2*j)%len(ACTIONS) for n in range(len(ACTIONS))]:
    action=ACTIONS[k];p=HERE/stage/(c['id']+'_'+action+f'_r{j}.json.gz')
    if canonical[c['id']][action]!=action:continue
    if p.exists():continue
    start=time.perf_counter();basis=rt.read(ref)['masters'];r=run(c,basis,action,stage!='validation_off',ref);r['complete_seconds']=time.perf_counter()-start;save(p,r)
    print(json.dumps(dict(stage=stage,case=c['id'],action=action,repetition=j,success=r['success'],seconds=r['complete_seconds'],fallbacks=r['fallbacks'])),flush=True)
 inputs.write(HERE/stage/'completion.json',dict(complete=True))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','training','validation','validation_off']);a=p.parse_args();collect(a.stage)
