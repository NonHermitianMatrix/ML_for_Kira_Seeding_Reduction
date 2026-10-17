"""Test the new seed-region control on development data only."""
import copy,json,time
from s00_policy import *
def main():
 choices=[None,[1,0,0,1,0,1],[2,0,0,1,0,1],[1,.5,0,1,.5,1],[0,0,0,1,0,1]]
 cases=[]
 for g in ['double_box','nonplanar_box','ladder3','sunrise','vacuum3','massless4']:
  for rank in ([2,4] if g in ['double_box','nonplanar_box'] else [2]):
   c=inputs.case(g,801,'rank'+str(rank),'development');c['targets']=c['targets'][:1];c['size']=1;cases.append(c)
 inputs.write(HERE/'development/protocol.json',dict(cases=cases,policies=choices,scope='Development only; no reserved timings.'))
 for c in cases:
  refpath=HERE/'references'/(c['id']+'.json.gz')
  if not refpath.exists():
   ref=rt.attempt(c,None,'expanded',timeout=90);save(refpath,rt.compact(ref))
  ref=rt.read(refpath)
  if not ref['success']:
   print(json.dumps(dict(case=c['id'],reference_failure=ref['status'])),flush=True);continue
  for i,theta in enumerate(choices):
   dest=HERE/'development'/(c['id']+'_p'+str(i)+'.json.gz')
   if dest.exists():continue
   r=run(c,ref['masters'],theta,refpath,timeout=60,recover=False);save(dest,r)
   print(json.dumps(dict(case=c['id'],policy=i,success=r['success'],seconds=r['complete_seconds'],seeds=r['seed_policy'],audit=r['attempts'][0].get('seed_audit'),equations=r['attempts'][0].get('counters'))),flush=True)
 inputs.write(HERE/'development/completion.json',dict(complete=True))
if __name__=='__main__':main()
