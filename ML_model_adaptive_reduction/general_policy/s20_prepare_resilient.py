"""Recover when a stored index basis is incomplete for new targets."""
from s14_prepare import *

def run(c,method):
 if len(c['definition']['propagators'])>31:
  return dict(success=False,status='unsupported_native_index_count',case=c['id'],method=method,complete_seconds=0.,first_action=None,attempts=[],basis_refreshed=False,process_timer_complete=False)
 start=time.perf_counter();deadline=start+110;attempts=[];seen={};coeff=None;basis=None;source=None;checks=0;refreshed=False
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
  # A checked basis from earlier targets can omit masters needed by this batch.
  # If even expanded seeding rejects it, discard that proposal and discover again.
  if source is not None and not (r['success'] and nontrivial(r)):
   refreshed=True;basis=None;a='expanded';r=call('refresh_rejected_basis','expanded')
  if r['success'] and nontrivial(r):
   if basis is None:basis=r['masters']
   coeff=r.get('coefficients',{})
   # The native target check uses the same basis and a different integral order.
   # It replaces the repeated broad discovery check; all identities remain exact.
   second=call('native_target_check','native',basis,2)
   if not second['success'] and a!='native':second=call('selected_target_check',a,basis,2)
   if not second['success']:second=call('expanded_target_check','expanded',basis,2)
  else:second=dict(success=False,status='no_nontrivial_reduction')
 success=False;status=second.get('status','incomplete')
 if r['success'] and second['success'] and nontrivial(r):
  success,checks=equal(coeff,second.get('coefficients',{}));status='verified' if success else 'coefficient_mismatch'
 return dict(success=success,status=status,case=c['id'],method=method,masters=basis or [],coefficients=coeff or {},attempts=attempts,coefficient_checks=checks,basis_refreshed=refreshed,source_case=source,cache_hit=source is not None,first_action=action,model_used=method in ['cached_learned','cached_risk'],inference_seconds=inference if method in ['cached_learned','cached_risk'] else 0,complete_seconds=time.perf_counter()-start,failed_attempts=sum(not a['result']['success'] for a in attempts),process_timer_complete=False)

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--input');p.add_argument('--output');a=p.parse_args()
 if a.initialize:raise ValueError('Use the frozen preparation cache; initialization is in s14.')
 else:
  request=READ(a.input)
  try:r=run(request['case'],request['method'])
  except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1800:])
  write(a.output,r)
