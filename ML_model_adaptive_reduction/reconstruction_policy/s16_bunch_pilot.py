"""Check evaluation batches and simpler targets before choosing training actions."""
from s00_reconstruction_common import *
from s06_measure import measured

def main():
 assert os.environ.get('JOB_ID') and read(HERE/'pilot_complete.json')['complete']
 old=previous();h=helper();maker=load('reconstruction_pilot_cases',PREVIOUS/'s03_cases.py')
 cases=maker.cases('development')
 for kind in ['double_box','nonplanar_box']:
  for shape in ['corner','numerator','dot']:
   c=h.inputs.case(kind,27109,shape,'development')
   c['id']='reconstruction_pilot_'+kind+'_'+shape
   cases.append(old.current().previous().previous().batch.canonical(c))
 for i,c in enumerate(cases):
  p=HERE/'references'/(c['id']+'.json.gz')
  if not p.exists():
   ref=read(PREVIOUS/'references'/(c['id']+'.json.gz')) if i<4 else old.reference_module().reference(c)
   write(p,ref)
  protected=p.with_name(c['id']+'_protected_basis.json.gz')
  ref=read(protected if protected.exists() else p)
  if not ref['success']:print(c['id'],'reference_failed',flush=True);continue
  settings=[('firefly',2),('firefly',4),('firefly',8),('firefly',16)]
  if i>=4:settings=[('previous',1),('firefly',1)]+settings
  for method,bunch in settings:
   dest=HERE/'development'/(c['id']+'_'+method+str(bunch)+'.json.gz')
   if dest.exists():continue
   r,t=measured(c,method,1,50,bunch);ok,n=h.compare(r,ref) if r.get('success') else (False,0)
   r.update(case=c['id'],application_seconds=t,verified=ok,coefficient_checks=n,method=method,bunch_size=bunch)
   write(dest,r);print(c['id'],method,bunch,round(t,4),ok,flush=True)
 write(HERE/'bunch_pilot_complete.json',dict(complete=True,bunch_sizes=[1,2,4,8,16],source_sha256=sha(HERE/'s16_bunch_pilot.py')))
if __name__=='__main__':main()
