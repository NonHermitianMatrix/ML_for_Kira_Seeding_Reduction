"""Use the published bounded native runner with a selected algebra backend."""
from s00_reconstruction_common import *
import inspect

BACKENDS=('symbolic','firefly','back')

def make_runner(backend,bunch=1):
 """Keep original preparation, admission checks, limits, exports and cleanup."""
 assert backend in BACKENDS and bunch in (1,2,4,8,16)
 native=helper().rt.native
 original=native.run
 source=inspect.getsource(original)
 def replace_once(old,new):
  nonlocal source
  assert source.count(old)==1,(old,source.count(old))
  source=source.replace(old,new)
 replace_once('run_initiate=True,run_triangular=True,run_back_substitution=True)',
  'run_initiate=True,run_triangular='+str(backend!='firefly')+
  ',run_back_substitution='+str(backend=='symbolic')+')\n'+
  ('  reduction["run_firefly"]='+repr(True if backend=='firefly' else 'back')+'\n' if backend!='symbolic' else '')+
  '  result["algebra_backend"]='+repr(backend)+';result["bunch_size"]='+str(bunch))
 start='  binary=ROOT/(".tools/kira-fast-expression/kira" if policy=="stock" else os.environ.get("KIRA_RUNTIME_BINARY",".tools/kira-integrated-runtime/kira"))'
 replace_once(start,'  binary=pathlib.Path('+repr(str(TOOLS/'kira'))+')')
 replace_once('[".tools/kira-sector-wide/kira",','[".tools/kira-reconstruction/kira",".tools/kira-sector-wide/kira",')
 replace_once('[str(binary),"--parallel="+str(threads),"jobs.yaml"]',
  '[str(binary),"--parallel="+str(threads),"--bunch_size='+str(bunch)+'","jobs.yaml"]')
 if backend!='symbolic':
  replace_once('  result["basis_admitted"]=',
   '  if not reference:result["verification_mode"]="finite_field_reconstruction_with_basis_admission" if basis is not None else "finite_field_reconstruction"\n  result["basis_admitted"]=')
 namespace=dict(original.__globals__)
 namespace['__file__']=__file__
 exec(compile(source,__file__,'exec'),namespace)
 run=namespace['run']
 run.original_source_sha256=hashlib.sha256(inspect.getsource(original).encode()).hexdigest()
 return run
