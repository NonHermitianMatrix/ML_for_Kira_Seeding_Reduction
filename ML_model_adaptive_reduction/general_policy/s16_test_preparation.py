"""Compare completed preparation workflows, keeping failures and all controls."""
from s00_common import *
from s14_prepare import P,equal
import subprocess
PYTHON=ROOT/'.tools/seed-model/venv/bin/python'

def call(c,m,rep):
 p=P/'model_test'/(c['id']+'_'+m+'_r'+str(rep)+'.json.gz')
 if p.exists():return READ(p)
 q=P/'requests'/(p.stem+'.json');out=p.with_name(p.name+'.pending.gz');write(q,dict(case=c,method=m));p.parent.mkdir(parents=True,exist_ok=True)
 start=time.perf_counter()
 proc=subprocess.run([str(PYTHON),str(HERE/'s14_prepare.py'),'--input',str(q),'--output',str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=145)
 r=READ(out) if out.exists() else dict(success=False,status='process_error',error=proc.stderr.decode()[-1200:])
 r.update(case=c['id'],method=m,complete_seconds=time.perf_counter()-start,process_timer_complete=True);write(p,r)
 q.unlink()
 if out.exists():out.unlink()
 print(c['id'],m,rep,r['success'],r.get('failed_attempts'),round(r['complete_seconds'],3),flush=True);return r

def main(worker):
 protocol=READ(P/'protocol.json');assert inputs.sha(P/'trained_model/freeze.json')==protocol['risk_sha256'];assert inputs.sha(HERE/'refit/trained_model/freeze.json')==protocol['model_sha256']
 for c in protocol['cases'][worker::2]:
  out=P/'coverage'/(c['id']+'.json')
  if out.exists():continue
  methods=protocol['methods'];first={};shift=sum(c['id'].encode())%len(methods)
  for m in methods[shift:]+methods[:shift]:first[m]=call(c,m,0)
  # Repeat every initially successful method, including newly recovered cases.
  success=[m for m in methods if first[m]['success']]
  for rep in [1,2]:
   shift=(sum(c['id'].encode())+rep)%len(methods)
   for m in methods[shift:]+methods[:shift]:
    if m in success:call(c,m,rep)
  pairs={}
  for a in methods:
   for b in methods:
    if a>=b or not first[a]['success'] or not first[b]['success']:continue
    same={tuple(x) for x in first[a]['masters']}=={tuple(x) for x in first[b]['masters']}
    agree,checks=equal(first[a]['coefficients'],first[b]['coefficients']) if same else (False,0)
    pairs[a+'/'+b]=dict(same_basis=same,agree=agree,coefficient_checks=checks)
  write(out,dict(case=c['id'],loops=len(c['definition']['loop_momenta']),group=c['topology_group'],first_success={m:r['success'] for m,r in first.items()},pair_checks=pairs))
 write(P/('worker_'+str(worker)+'_complete.json'),dict(complete=True,risk_sha256=protocol['risk_sha256'],model_sha256=protocol['model_sha256']))
if __name__=='__main__':main(int(sys.argv[1]))
