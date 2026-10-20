"""Measure backend costs for training and separate validation requests."""
from s00_reconstruction_common import *
from s06_measure import measured
from s10_cases import cases,features
from s20_reference import reference
import random,statistics,copy

def main():
 phase=sys.argv[1];worker=int(sys.argv[2])
 assert phase in ['training','validation'] and worker in [0,1]
 assert os.environ.get('JOB_ID')
 config=read(HERE/'actions.json')
 h=helper();old=previous()
 for c in cases(phase)[worker::2]:
  refpath=HERE/'references'/(c['id']+'.json.gz')
  if refpath.exists():ref=read(refpath)
  else:
   ref=reference(c);write(refpath,ref)
  if not ref['success']:
   write(HERE/phase/(c['id']+'_reference_failure.json'),dict(case=c['id'],success=False,reference=ref))
   print(c['id'],'reference_failed',flush=True);continue
  actions=list(config['actions']);random.Random(c['id']).shuffle(actions)
  for action in actions:
   method,bunch=config['settings'][action]
   dest=HERE/phase/(c['id']+'_'+action+'.json.gz')
   if dest.exists():continue
   times=[];checked=[];checks=0;failures=[]
   for rep in range(3 if phase=='validation' else 1):
    r,seconds=measured(c,method,worker,config['deadline'],bunch)
    ok,n=h.compare(r,ref) if r.get('success') else (False,0)
    times.append(seconds);checked.append(ok);checks+=n
    if not ok:failures.append(dict(repetition=rep,result=copy.deepcopy(r)))
   r.update(case=c['id'],application_seconds=statistics.mean(times),verified=all(checked),coefficient_checks=checks,action=action,features=features(c),repetition_seconds=times,repetition_verified=checked,failure_fraction=sum(not v for v in checked)/len(checked),failed_repetitions=failures)
   write(dest,r);print(c['id'],action,round(seconds,4),ok,flush=True)
   assert not any(x['result'].get('success') for x in failures),(c['id'],action,'coefficient mismatch')
 write(HERE/(phase+str(worker)+'_complete.json'),dict(complete=True,actions_sha256=sha(HERE/'actions.json'),cases_source_sha256=sha(HERE/'s10_cases.py')))
if __name__=='__main__':main()
