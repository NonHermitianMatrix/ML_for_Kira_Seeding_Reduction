"""Reserved complete-time comparisons and analytic regression checks."""
from s00_triangle_common import *
from s04_triangle_measure import measured,native_triangle,compare
import random,socket

def main(w):
 assert os.environ.get('JOB_ID')
 p=read(HERE/'test_protocol.json.gz');assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert all(sha(HERE/n)==s for n,s in p['source_sha256'].items())
 for c in p['cases'][w::2]:
  dest=HERE/'model_test'/(c['id']+'.json.gz')
  if dest.exists():continue
  ref,ref_seconds=measured(c,'previous',w)
  native=None
  if c.get('test_group')=='native':
   ref,ref_seconds=measured(c,'symbolic_prior',w)
  if c['topology_group']=='one_scale_triangle' and len(c['definition']['loop_momenta'])==1:
   native=native_triangle(c)
   if native.get('success'):ref=native
  write(HERE/'test_references'/(c['id']+'.json.gz'),ref)
  row=dict(case=c,reference_success=ref.get('success',False),reference_seconds=ref_seconds,native_reference=native,results={},times={},verified={},checks=0,host=socket.gethostname())
  for rep in range(p['repetitions']):
   actions=list(p['actions']);random.Random(c['id']+str(rep)).shuffle(actions)
   for a in actions:
    r,t=measured(c,a,w);ok,n=compare(c,r,ref) if ref.get('success') and r.get('success') else (False,0)
    row['results'].setdefault(a,[]).append(r);row['times'].setdefault(a,[]).append(t);row['verified'].setdefault(a,[]).append(ok);row['checks']+=n
  write(dest,row);print(c['id'],{a:round(sum(t)/len(t),4) for a,t in row['times'].items()},'verified',all(all(x) for x in row['verified'].values()),flush=True)
  assert all(all(x) for x in row['verified'].values()),c['id']
 for c in p['regression'][w::2]:
  dest=HERE/'regression'/(c['id']+'.json.gz')
  if dest.exists():continue
  ref=read(PRIOR/'test_references'/(c['id']+'.json.gz'));r,t=measured(c,'integrated',w);ok,n=compare(c,r,ref)
  write(dest,dict(case=c['id'],success=ok,seconds=t,checks=n,result=r));assert ok,c['id']
 write(HERE/f'test{w}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'test_protocol.json.gz')))
if __name__=='__main__':main(int(sys.argv[1]))
