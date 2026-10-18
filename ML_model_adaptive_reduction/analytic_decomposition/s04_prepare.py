"""Check the recurrence and prepare independent native master-index sets."""
from s01_common import *
from s03_cases import polygon
from s02_runtime import run
import itertools,copy,fcntl,traceback
reference_old=h.inputs.module('analytic_old_reference',h.BLOCK/'s11_extension_test.py').reference

def native(c,basis=None,ordering=2,expanded=True):
 with h.rt.environment():
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  return h.rt.compact(h.rt.native.run(c,c['size'],'native',HERE/'unused',timeout=45,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=h.inputs.bounds(c,'expanded' if expanded else 'native'),ordering=ordering,threads=1))

def add_basis(c,masters):
 p=HERE/'basis_registry.json'
 with (HERE/'.basis_lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);r=READ(p) if p.exists() else {};k=signature(c);stored=h.old.store_basis(c,masters)
  if k in r:stored=sorted(set(map(tuple,stored))|set(map(tuple,r[k]['basis'])))
  r[k]=dict(basis=[list(x) for x in stored],source='Independent native reductions; indices only.');write(p,r)

def reference(c):
 parts=h.split_blocks(c);blocks=[];memo={}
 for part in parts:
  sub=part['case'];identity=json.dumps([sub['definition'],sub['targets']],sort_keys=True)
  if identity not in memo:
   if recurrence(sub) is None or h.exact(sub) is not None:
    r=reference_old(sub);r=r['blocks'][0]['result'] if r.get('success') else r
   else:
    n=len(sub['definition']['propagators']);allunits=[list(a) for a in itertools.product([0,1],repeat=n) if any(a)]
    aug=copy.deepcopy(sub);aug['targets']=[list(a) for a in dict.fromkeys(map(tuple,sub['targets']+allunits))];aug['size']=len(aug['targets'])
    a=native(aug,ordering=2);b=native(aug,basis=a.get('masters') if a['success'] else None,ordering=1,expanded=False)
    ok,checks=h.equal(a.get('coefficients',{}),b.get('coefficients',{})) if a['success'] and b['success'] else (False,0)
    r=dict(a,success=ok,status='independent_native_agreement' if ok else 'native_reference_failed',reference_check=b,coefficient_checks=checks)
    if ok:
     add_basis(sub,a['masters']);r['coefficients']={h.label(t):a['coefficients'][h.label(t)] for t in sub['targets']}
   memo[identity]=r
  r=memo[identity];blocks.append(dict(indices=part['indices'],case=sub,result=r))
  if not r['success']:return dict(success=False,status=r.get('status'),blocks=blocks)
 return dict(success=True,status='reference_completed',blocks=blocks)

def pilot():
 checks=[]
 for n in [2,3,4,5]:
  c=polygon(n,2401,1);ref=reference(c);out=run(c);ok,count=h.compare(out,ref)
  write(HERE/'pilot'/f'n{n}.json.gz',dict(case=c,reference=ref,result=out,verified=ok,checks=count))
  assert ok,(n,ref.get('status'),out.get('status'));assert out['blocks'][0]['result']['route']=='one_loop_cayley_recurrence';checks.append(dict(n=n,checks=count,route=out['blocks'][0]['result']['route']))
 c=polygon(2,2401,1,True);ref=reference(c);out=run(c);ok,count=h.compare(out,ref)
 write(HERE/'pilot/symbolic.json.gz',dict(case=c,reference=ref,result=out,verified=ok,checks=count));assert ok
 # Repeated indices, numerator, unsupported cut, and singular matrices must
 # return to the established exact solver instead of dividing by zero.
 c=polygon(2,2401,1);c['definition']['scalarproduct_rules'][0][1]='0';c['definition']['propagators'][1]['mass_squared']=c['definition']['propagators'][0]['mass_squared'];assert recurrence(c) is None
 c=polygon(2,2401,1);c['targets'][0][0]=-1;assert recurrence(c) is None
 c=polygon(2,2401,1);c['definition']['cut_propagators']=[1];assert recurrence(c) is None
 write(HERE/'pilot_validation.json',dict(complete=True,native_checks=checks,symbolic_checks=count,singular_and_unsupported_fallback=True))

def prepare(worker):
 assert READ(HERE/'pilot_validation.json')['complete'];p=READ(HERE/'protocol.json')
 for i,c in enumerate(p['cases']):
  if i%2!=worker:continue
  dest=HERE/'references'/(c['id']+'.json.gz')
  if dest.exists():continue
  start=time.perf_counter()
  try:r=reference(c)
  except Exception as e:r=dict(success=False,status='reference_exception',error=repr(e),traceback=traceback.format_exc()[-1200:])
  r['preparation_seconds']=time.perf_counter()-start;write(dest,r)
  print(json.dumps(dict(case=c['id'],success=r['success'],seconds=r['preparation_seconds'])),flush=True)
 write(HERE/f'prepare_{worker}_complete.json',dict(complete=True))
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else prepare(int(sys.argv[1]))
