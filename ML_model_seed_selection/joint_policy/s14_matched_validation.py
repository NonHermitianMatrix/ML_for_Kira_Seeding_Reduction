"""Repeat one validation profile with every configuration on the same worker."""
from s00_engine import *

def main():
 protocol=rt.read(HERE/'protocols/nonplanar_box.json');actions=protocol['actions']+['previous'];count=0
 for i,c in enumerate(protocol['validation']):
  if '_h922_' not in c['id']:continue
  for rep in range(3):
   order=actions[(i+rep)%len(actions):]+actions[:(i+rep)%len(actions)]
   for name in order:
    r=evaluate(c,name,'matched_validation',rep);assert r['success'] and r['worker']==os.uname().nodename;count+=1
 save(HERE/'matched_validation/completion.json',dict(complete=True,records=count,worker=os.uname().nodename,profile=922))

if __name__=='__main__':main()
