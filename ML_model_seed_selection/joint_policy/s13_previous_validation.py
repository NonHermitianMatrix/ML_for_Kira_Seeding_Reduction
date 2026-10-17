"""Match the preceding application to the second validation worker's costs."""
from s00_engine import *

def main():
 protocol=rt.read(HERE/'protocols/nonplanar_box.json');count=0
 for c in protocol['validation']:
  if '_h922_' not in c['id']:continue
  baseline=rt.read(HERE/'validation'/(c['id']+'_native_r0.json.gz'))
  assert baseline['worker']==os.uname().nodename
  for rep in range(3):
   r=evaluate(c,'previous','validation',rep);assert r['success'] and r['worker']==baseline['worker'];count+=1
 save(HERE/'validation/previous_helper_completion.json',dict(complete=True,records=count,worker=os.uname().nodename,profile=922))

if __name__=='__main__':main()
