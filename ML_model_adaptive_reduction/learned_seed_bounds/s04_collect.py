"""Freeze disjoint inputs, then collect measured training and validation costs."""
import argparse,json,time
from s00_inputs import *
from s02_development import reference
import s01_runtime as rt

def freeze():
 p=HERE/'protocol.json'
 if p.exists():return rt.read(p)
 d=dict(splits={s:make(s) for s in ['training','validation','reserved']},actions=ACTIONS,
        binary=sha(rt.BINARY),features=FEATURE_NAMES,
        repetitions=5,methods=['native','fixed','learned'],
        controls='Same exact implementation; all earlier ML disabled. Fixed graph choices may use training and validation costs.',
        reference='Expanded seeds, independently checked with one additional numerator rank. Basis supplied during application timings.',
        split='Distinct momentum parameters and shifted target positions; graph structures shared. No claim of unseen topology generalization.',
        primary='Sum of per-case median complete times. Keep failures and identity-only cases separate. Bootstrap by graph; also show every graph and repetition.',
        timeout=90,reference_timeout=120,tree_memory_mib=5200,scratch_mib=32,
        frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
 assert not(set(c['id'] for c in d['splits']['training'])&set(c['id'] for c in d['splits']['reserved']))
 write(p,d);return d

def collect(split):
 d=freeze();out=HERE/split;out.mkdir(exist_ok=True)
 for i,c in enumerate(d['splits'][split]):
  ref=reference(c)
  if ref is None:
   write(out/(c['id']+'_excluded.json'),dict(case=c['id'],reason='Reference or independent check failed within resource limits.'))
   continue
  basis=rt.read(ref)['masters'];offset=i%len(ACTIONS);order=ACTIONS[offset:]+ACTIONS[:offset];seen={}
  for a in order:
   p=out/(c['id']+'_'+a+'.json.gz');key=(tuple(bounds(c,a)),truncation(c,a))
   if p.exists():seen[key]=p;continue
   if key in seen:
    r=rt.read(seen[key]);r['identical_configuration_from']=seen[key].name;r['requested_action']=a
   else:
    r=rt.run(c,basis,first=a,reference=ref);r['requested_action']=a
   rt.save(p,r);seen[key]=p
   print(json.dumps(dict(stage=split,case=c['id'],action=a,success=r['success'],seconds=r['complete_seconds'],fallbacks=r['fallbacks'],identical_configuration='identical_configuration_from' in r)),flush=True)
 write(out/'completion.json',dict(complete=True,cases=len(d['splits'][split])))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--split',choices=['training','validation','both'],default='both');a=p.parse_args()
 freeze()
 if not a.freeze:
  for s in (['training','validation'] if a.split=='both' else [a.split]):collect(s)
