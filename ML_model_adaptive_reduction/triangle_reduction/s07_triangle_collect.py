"""Measure fresh training and validation requests with complete retry costs."""
from s00_triangle_common import *
from s02_triangle_cases import native_cases
from s04_triangle_measure import measured,compare
import random,statistics

def features(c):
 prior();from s10_cases import features as old
 return old(c)

def main(phase,w):
 assert os.environ.get('JOB_ID') and phase in ['training','validation']
 cfg=read(HERE/'learning_protocol.json');actions=cfg['actions']
 for c in native_cases(phase)[w::2]:
  dest=HERE/phase/(c['id']+'.json.gz')
  if dest.exists():continue
  ref,t=measured(c,'previous',w);write(HERE/'references'/(c['id']+'.json.gz'),ref)
  row=dict(case=c,features=features(c),actions={},reference_seconds=t,reference_success=ref.get('success',False))
  if not ref.get('success'):
   write(dest,row);print(c['id'],'reference failure',flush=True);continue
  order=['baseline'] if c['topology_group'] in cfg.get('guarded_structures',[]) else list(actions);random.Random(c['id']).shuffle(order)
  for a in order:
   times=[];records=[];checks=0
   for rep in range(cfg['repetitions'][phase]):
    r,t=measured(c,a,w);ok,n=compare(c,r,ref) if r.get('success') else (False,0);checks+=n
    records.append(dict(result=r,verified=ok));times.append(t)
    if not ok:write(HERE/'failed_comparisons'/(c['id']+'_'+a+'_'+str(rep)+'.json.gz'),dict(case=c,result=r,reference=ref,seconds=t))
    assert ok or not r.get('success'),(c['id'],a,'coefficient mismatch')
   row['actions'][a]=dict(seconds=statistics.mean(times),times=times,records=records,checks=checks,verified=all(r['verified'] for r in records),first_attempt_failures=sum('new_failed_attempt' in r['result'] for r in records))
  write(dest,row);print(c['id'],[(a,round(r['seconds'],3),r['verified']) for a,r in row['actions'].items()],flush=True)
 write(HERE/(phase+str(w)+'_complete.json'),dict(complete=True,protocol_sha256=sha(HERE/'learning_protocol.json')))
if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]))
