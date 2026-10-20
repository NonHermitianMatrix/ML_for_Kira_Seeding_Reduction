"""Pilot formula and native choices before fitting or reserved measurements."""
from s00_triangle_common import *
from s02_triangle_cases import triangle_cases,native_cases
from s04_triangle_measure import measured,native_triangle,compare

def main(w):
 assert os.environ.get('JOB_ID')
 for c in triangle_cases('development')[w::2]:
  if len(c['definition']['loop_momenta'])>1:continue
  ref=native_triangle(c);write(HERE/'development'/(c['id']+'_reference.json.gz'),ref)
  for action in ['previous','integrated']:
   r,t=measured(c,action,w);ok,n=compare(c,r,ref) if ref.get('success') else (False,0)
   write(HERE/'development'/(c['id']+'_'+action+'.json.gz'),dict(case=c,result=r,seconds=t,verified=ok,checks=n));print(c['id'],action,t,ok,flush=True)
 for c in native_cases('development')[w::2]:
  r,t=measured(c,'previous',w);ref=r;write(HERE/'development'/(c['id']+'_reference.json.gz'),dict(case=c,result=r,seconds=t))
  for action in ['ff1','ff4','ff8','ff16']:
   r,t=measured(c,action,w);ok,n=compare(c,r,ref) if ref.get('success') else (False,0)
   write(HERE/'development'/(c['id']+'_'+action+'.json.gz'),dict(case=c,result=r,seconds=t,verified=ok,checks=n));print(c['id'],action,round(t,4),ok,flush=True)
 write(HERE/f'development{w}_complete.json',dict(complete=True))
if __name__=='__main__':main(int(sys.argv[1]))
