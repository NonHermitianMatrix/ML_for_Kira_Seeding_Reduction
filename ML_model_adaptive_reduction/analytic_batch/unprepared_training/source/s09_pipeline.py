"""Run dependent training stages only after their required checks pass."""
from s00_batch_common import *

def collect(worker):
 for w in [0,1]:assert read(HERE/f'development_{w}_complete.json')['complete']
 for symbolic in [False,True]:assert read(HERE/'development'/('triangle_'+str(symbolic)+'.json.gz'))['verified']
 from s03_cases import batches
 for i in [0,3,6,8,11,14]:
  c=batches(3001,'development')[i];assert read(HERE/'references'/(c['id']+'.json.gz'))['success']
 from s05_collect import main
 main('training',worker);main('validation',worker)

if __name__=='__main__':collect(int(sys.argv[1]))
