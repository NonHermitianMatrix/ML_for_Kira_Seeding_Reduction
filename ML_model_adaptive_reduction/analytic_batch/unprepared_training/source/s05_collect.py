"""Collect complete reduction costs before selecting any new policy."""
from s00_batch_common import *
from s03_cases import batches,triangle
from s04_measure import measured,prepare

def main(phase,worker):
 if phase=='development':cases=[batches(3001,phase)[i] for i in [0,3,6,8,11,14]];reps=1
 elif phase=='training':cases=batches(3011,phase)+batches(3019,phase);reps=1
 elif phase=='validation':cases=batches(3037,phase);reps=2
 else:raise ValueError(phase)
 if phase=='development' and worker==0:
  from s01_triangle import reduce
  for symbolic in [False,True]:
   c=triangle(3001,symbolic=symbolic);ref=prepare(c);r=reduce(c);ok,n=legacy().h.equal(r['coefficients'],ref['blocks'][0]['result'].get('coefficients',{})) if ref['success'] else (False,0)
   write(HERE/'development'/('triangle_'+str(symbolic)+'.json.gz'),dict(case=c,result=r,reference=ref,verified=ok,coefficient_checks=n));print(json.dumps(dict(triangle=symbolic,verified=ok,checks=n)),flush=True);assert ok
 for i,c in enumerate(cases):
  if i%2!=worker:continue
  ref=prepare(c)
  for rep in range(reps):
   methods=ACTIONS[(i+rep)%len(ACTIONS):]+ACTIONS[:(i+rep)%len(ACTIONS)]
   for method in methods:
    r=measured(c,method,rep,ref,phase)
    print(json.dumps(dict(case=c['id'],method=method,rep=rep,verified=r['independently_verified'],seconds=r['complete_process_and_check_seconds'])),flush=True)
 write(HERE/(phase+'_'+str(worker)+'_complete.json'),dict(complete=True))
if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]))
