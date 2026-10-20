"""Run a paired ML ablation without changing the frozen four-method comparison."""
from s00_reconstruction_common import *
from s20_reference import reference
import inspect,statistics,socket
import s06_measure

def measured_control():
 # Reuse the already checked process timer, adding only this executable to its
 # allowed entry names. Preserve the original timer and frozen protocol files.
 source=inspect.getsource(s06_measure.measured)
 old="assert entry in ['s05_runtime.py','s15_deploy.py']"
 assert source.count(old)==1
 source=source.replace(old,"assert entry in ['s05_runtime.py','s15_deploy.py','s33_retained_ml.py']")
 namespace=dict(s06_measure.__dict__);exec(compile(source,__file__,'exec'),namespace)
 return namespace['measured']

def freeze():
 p=read(HERE/'test_protocol.json.gz');assert not read(HERE/'trained_model/policy.json')['enabled']
 protocol=dict(cases=[c for c in p['cases'] if c['test_group']=='native'],methods=['retained_ml','retained_fixed'],repetitions=3,parent_protocol_sha256=sha(HERE/'test_protocol.json.gz'),sources={f.name:sha(f) for f in HERE.glob('s*.py') if int(f.name[1:3])<=24 or 33<=int(f.name[1:3])<=34},models=p['model_sha256'],binary_sha256=p['binary_sha256'],decision='Measure inherited learned choices against the preceding all-fixed dispatch with the newly validated algebra settings shared. No new fitting or selection uses these outcomes.')
 write(HERE/'retained_protocol.json.gz',protocol)
 print('Retained-ML comparison fixed',len(protocol['cases']),'requests',flush=True)

def main(worker):
 p=read(HERE/'retained_protocol.json.gz');assert all(sha(HERE/n)==v for n,v in p['sources'].items())
 assert all(sha(HERE/'trained_model'/n)==v for n,v in p['models'].items())
 assert sha(TOOLS/'kira')==p['binary_sha256']
 assert sha(HERE/'test_protocol.json.gz')==p['parent_protocol_sha256']
 for w in [0,1]:assert read(HERE/f'test{w}_complete.json')['complete']
 timer=measured_control();h=helper()
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'retained_ml_test'/(c['id']+'.json.gz')
  if dest.exists():continue
  ref=read(HERE/'test_references'/(c['id']+'.json.gz'))
  methods=p['methods'];times={m:[] for m in methods};success={m:[] for m in methods};saved={};failures=[];checks=0;actions={m:[] for m in methods}
  for rep in range(p['repetitions']):
   order=methods if (rep+i)%2==0 else methods[::-1]
   for m in order:
    r,elapsed=timer(c,m,worker,90,entry='s33_retained_ml.py')
    ok,n=h.compare(r,ref) if ref.get('success') else (False,0)
    times[m].append(elapsed);success[m].append(ok);saved[m]=r;checks+=n
    actions[m].append([a.get('seed_policy',a.get('action')) for b in r.get('blocks',[]) for a in b['result'].get('attempts',[])])
    if not ok:failures.append(dict(method=m,repetition=rep,result=r))
    if ref.get('success') and r.get('success') and not ok:
     write(HERE/'disagreements'/(c['id']+'_retained_'+m+'.json.gz'),dict(case=c,result=r,reference=ref))
     raise AssertionError((c['id'],m,'coefficient disagreement'))
  row=dict(case=c['id'],topology=c['topology_group'],loops=len(c['definition']['loop_momenta']),worker_host=socket.gethostname(),times=times,success=success,reference_success=ref.get('success'),results=saved,failed_applications=failures,checks=checks,actions=actions,median_seconds={m:statistics.median(v) for m,v in times.items()})
  write(dest,row);print('retained',c['id'],row['median_seconds'],{m:all(v) for m,v in success.items()},flush=True)
 write(HERE/f'retained{worker}_complete.json',dict(complete=True,protocol_sha256=sha(HERE/'retained_protocol.json.gz')))

if __name__=='__main__':
 if sys.argv[1]=='prepare':freeze()
 else:main(int(sys.argv[1]))
