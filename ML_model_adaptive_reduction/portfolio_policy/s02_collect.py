"""Collect complete measured costs on separate physical parameter profiles."""
from s00_common import *
import argparse,subprocess
PYTHON=ROOT/'.tools/seed-model/venv/bin/python'
def call(c,m,p,basis=None,reference=None):
 if p.exists():return read(p)
 q=HERE/'requests'/(p.stem+'.json');write(q,dict(case=c,method=m,basis=basis,reference=str(reference) if reference else None))
 used=allocated();assert used+2*1024**2<24*1024**2
 worker_output=p.with_name(p.name+'.pending.gz')
 start=time.perf_counter();r=subprocess.run([str(PYTHON),str(HERE/'s01_application.py'),'--input',str(q),'--output',str(worker_output)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=310)
 elapsed=time.perf_counter()-start
 out=read(worker_output) if worker_output.exists() else dict(success=False,status='worker_exit',error=r.stderr.decode()[-1500:])
 out.update(complete_seconds=elapsed,case=c['id'],method=m,process_timer_complete=True);write(p,out);q.unlink()
 if worker_output.exists():worker_output.unlink()
 print(c['id'],m,out['success'],round(elapsed,3),flush=True);return out

def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz');r=call(c,'reference',p)
 if not r['success']:return None
 cp=HERE/'references'/(c['id']+'_check.json.gz');ch=call(c,'check',cp,r['masters'],p)
 return p if ch['success'] else None

def collect(split,worker):
 protocol=freeze();cases=protocol['splits'][split][worker::2]
 for i,c in enumerate(cases):
  marker=HERE/split/(c['id']+'_complete.json')
  if marker.exists():continue
  ref=reference(c)
  if ref is None:
   write(marker,dict(success=False,status='reference_unavailable'));continue
  basis=read(ref)['masters'];reps=2 if split=='validation' else 1
  for rep in range(reps):
   shift=(sum(c['id'].encode())+rep)%len(ACTIONS);order=ACTIONS[shift:]+ACTIONS[:shift];seen={}
   for a in order:
    p=HERE/split/(c['id']+'_'+a+'_r'+str(rep)+'.json.gz');key=(tuple(inputs.bounds(c,a)),inputs.truncation(c,a))
    if p.exists():seen[key]=p;continue
    if key in seen:
     r=read(seen[key]);r.update(requested_action=a,identical_configuration_from=seen[key].name);write(p,r)
    else:call(c,'action_'+a,p,basis,ref)
    seen[key]=p
  if split=='validation':
   for rep in range(2):call(c,'previous',HERE/split/(c['id']+'_previous_r'+str(rep)+'.json.gz'),basis,ref)
  write(marker,dict(success=True,status='complete'))
 write(HERE/(split+'_'+str(worker)+'_complete.json'),dict(complete=True))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('split');ap.add_argument('worker',type=int);a=ap.parse_args();collect(a.split,a.worker)
