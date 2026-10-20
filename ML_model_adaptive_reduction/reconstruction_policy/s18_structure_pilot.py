"""Test native two-point and vacuum structures before training selection."""
from s00_reconstruction_common import *
from s06_measure import measured

def main():
 assert os.environ.get('JOB_ID') and read(HERE/'build.json')['complete']
 old=previous();h=helper()
 for kind in ['sunrise','vacuum3']:
  for shape in ['corner','dot']:
   c=h.inputs.case(kind,27143,shape,'development')
   c['id']='reconstruction_structure_'+kind+'_'+shape
   refpath=HERE/'references'/(c['id']+'.json.gz')
   if not refpath.exists():
    try:ref=old.reference_module().reference(c)
    except Exception as e:ref=dict(success=False,error=repr(e))
    write(refpath,ref)
   protected=refpath.with_name(c['id']+'_protected_basis.json.gz')
   ref=read(protected if protected.exists() else refpath)
   if not ref['success']:print(c['id'],'reference_failed',flush=True);continue
   for method,bunch in [('previous',1),('firefly',1),('firefly',2),('firefly',4),('firefly',8),('firefly',16)]:
    dest=HERE/'development'/(c['id']+'_'+method+str(bunch)+'.json.gz')
    if dest.exists():continue
    r,t=measured(c,method,0,50,bunch);ok,n=h.compare(r,ref) if r.get('success') else (False,0)
    r.update(case=c['id'],application_seconds=t,verified=ok,coefficient_checks=n,method=method,bunch_size=bunch)
    write(dest,r);print(c['id'],method,bunch,round(t,4),ok,flush=True)
 write(HERE/'structure_pilot_complete.json',dict(complete=True,bunch_sizes=[1,2,4,8,16],source_sha256=sha(HERE/'s18_structure_pilot.py')))
if __name__=='__main__':main()
