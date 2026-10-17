"""Evaluate the second nonplanar validation profile on one bounded worker."""
from s00_engine import *

def main():
 g='nonplanar_box';protocol=rt.read(HERE/'protocols'/(g+'.json'));actions=protocol['actions'];count=0
 for i,c in enumerate(protocol['validation']):
  if '_h922_' not in c['id']:continue
  for rep in range(3):
   order=actions[(i+rep)%len(actions):]+actions[:(i+rep)%len(actions)]
   for name in order:
    r=evaluate(c,name,'validation',rep);assert r['success'];count+=1
 # The main training job reads these completed costs without changing any value.
 save(HERE/'validation/helper_completion.json',dict(complete=True,records=count,profile=922,candidate_order_preserved=True))

if __name__=='__main__':main()
