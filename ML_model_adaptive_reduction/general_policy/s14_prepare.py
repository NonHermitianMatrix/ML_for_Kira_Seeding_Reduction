"""Reduce without repeated large reference preparation, using checked basis indices."""
from s00_common import *
import s02_application as shared
from contextlib import contextmanager
shared.HERE=HERE/'refit'
P=HERE/'preparation'

@contextmanager
def exact_runtime():
 old=rt.native.run
 def run(*args,**kw):
  os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira')
  os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
  return old(*args,**kw)
 rt.native.run=run
 try:yield
 finally:rt.native.run=old


def key(c):
 return hashlib.sha256(inputs.signature(c).encode()).hexdigest()

def initialize():
 if (P/'protocol.json').exists():return
 cache={}
 for c in READ(HERE/'protocol.json')['reserved']:
  q=HERE/'coverage'/(c['id']+'.json')
  if READ(q)['status']!='verified':continue
  ref=HERE/'references'/(c['id']+'.json.gz');r=READ(ref)
  if not r['masters']:continue
  item=dict(basis=r['masters'],source_case=c['id'],reference=str(ref.relative_to(ROOT)),reference_sha256=inputs.sha(ref),check_sha256=inputs.sha(ref.with_name(c['id']+'_check.json.gz')))
  k=key(c)
  if k not in cache or len(item['basis'])<len(cache[k]['basis']):cache[k]=item
 # Defined before the new measurements. Both new controls use the same cache.
 chosen=[]
 for c in cases(1237):
  L=len(c['definition']['loop_momenta']);g=re.sub(r'_L[0-9]+$', '', c['topology_group'])
  if len(c['definition']['propagators'])>31:continue
  orders={'vacuum_one_mass':[1,2,4,5,6,7],'vacuum_all_mass':[2,4,5,6,7],'propagator_massless':[2,3,4,5,6],'propagator_massive':[2,3,4,5,6],'ladder':[1,2,3,4,5],'bubble_box':[2,3,4,5],'nonplanar_box':[2],'pentagon':[1],'one_mass_box':[1]}
  if L in orders.get(g,[]) and c['shape']==('dots' if L%2 else 'mixed'):chosen.append(c)
 write(P/'basis_cache.json',dict(entries=cache,scope='Prior profile 1201, checked reference and enlarged-region agreement. Reuse indices only, never coefficients. A new target must pass two exact reductions.'))
 write(P/'protocol.json',dict(cases=chosen,profile=1237,repetitions=3,integral_ordering_bits=128,total_budget_seconds=110,methods=['expanded','cached_native','cached_learned','cached_risk'],model_sha256=inputs.sha(HERE/'refit/trained_model/freeze.json'),risk_sha256=inputs.sha(P/'trained_model/freeze.json'),cache_sha256=inputs.sha(P/'basis_cache.json'),timing='Fresh process; full discovery or basis lookup, prediction, exact reduction, independent target check, recovery, and exit. Identical global deadline and per-call cap.',scope='Compare all declared outcomes; timing ratios require three complete matching outputs and the same master-index basis. A timeout is not a successful fast result.'))
 print('PREPARATION PROTOCOL',len(chosen),'cached structures',len(cache),flush=True)


def choose(c):
 f=READ(HERE/'refit/trained_model/freeze.json');s=shared.predict(f['model'],features(c));a=f['selection']['anchor'];i=min(range(len(s)),key=s.__getitem__)
 return ACTIONS[i if s[i]<s[a]-f['selection']['margin'] else a]

def equal(a,b):
 if set(a)!=set(b):return False,0
 checks=0
 for t,row in a.items():
  for m in set(row)|set(b[t]):
   x,y=row.get(m,'0'),b[t].get(m,'0');checks+=1
   if x!=y:
    import sympy as sp
    if sp.cancel(sp.sympify(x.replace('^','**'),rational=True)-sp.sympify(y.replace('^','**'),rational=True))!=0:return False,checks
 return True,checks

def nontrivial(r):return any(row and row!={t:'1'} for t,row in r.get('coefficients',{}).items())

def run(c,method):
 start=time.perf_counter();deadline=start+110;attempts=[];seen={};coeff=None;basis=None;source=None;checks=0
 action=choose(c) if method=='cached_learned' else 'native';inference=time.perf_counter()-start
 def call(tag,action,basis=None,ordering=1,enlarge=False):
  b=inputs.bounds(c,action)
  if enlarge:b[1]+=1
  trunc=inputs.truncation(c,action)
  signature=json.dumps([b,trunc,basis,ordering],sort_keys=True)
  if signature in seen:return seen[signature]
  left=deadline-time.perf_counter()
  if left<12:return dict(success=False,status='total_time_budget')
  with exact_runtime(),rt.environment():
   r=rt.native.run(c,c['size'],'native',P/'unused',timeout=min(60,left),margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=ordering,threads=1,truncate=trunc)
  r=rt.compact(r);attempts.append(dict(tag=tag,action=action,ordering=ordering,result=r));seen[signature]=r;return r
 if method=='expanded':
  r=call('discovery','expanded')
  if r['success']:
   basis=r['masters'];coeff=r.get('coefficients',{});second=call('enlarged_check','expanded',basis,2,True)
  else:second=r
 else:
  entry=READ(P/'basis_cache.json')['entries'].get(key(c))
  if entry:basis=entry['basis'];source=entry['source_case']
  if method=='cached_risk':
   import s15_risk
   tick=time.perf_counter();action=s15_risk.choose(c,basis);inference=time.perf_counter()-tick
  # Try the selected compact region first. Only incomplete attempts expand it.
  r=dict(success=False,status='not_started')
  for a in dict.fromkeys([action,'native','expanded']):
   r=call('cached_reduction' if basis is not None else 'compact_discovery',a,basis)
   if r['success'] and nontrivial(r):break
  if r['success'] and nontrivial(r):
   if basis is None:basis=r['masters']
   coeff=r.get('coefficients',{})
   # The native target check uses the same basis and a different integral order.
   # It replaces the repeated broad discovery check; all identities remain exact.
   second=call('native_target_check','native',basis,2)
   if not second['success'] and a!='native':second=call('selected_target_check',a,basis,2)
  else:second=dict(success=False,status='no_nontrivial_reduction')
 success=False;status=second.get('status','incomplete')
 if r['success'] and second['success'] and nontrivial(r):
  success,checks=equal(coeff,second.get('coefficients',{}));status='verified' if success else 'coefficient_mismatch'
 return dict(success=success,status=status,case=c['id'],method=method,masters=basis or [],coefficients=coeff or {},attempts=attempts,coefficient_checks=checks,source_case=source,cache_hit=source is not None,first_action=action,model_used=method in ['cached_learned','cached_risk'],inference_seconds=inference if method in ['cached_learned','cached_risk'] else 0,complete_seconds=time.perf_counter()-start,failed_attempts=sum(not a['result']['success'] for a in attempts),process_timer_complete=False)

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--input');p.add_argument('--output');a=p.parse_args()
 if a.initialize:initialize()
 else:
  request=READ(a.input)
  try:r=run(request['case'],request['method'])
  except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1800:])
  write(a.output,r)
