"""Apply checked basis sets, exact block formulas, and learned native seed bounds."""
from s00_common import *
from s01_families import split_blocks
from s02_model import choose
from s03_runtime import formula
import s07_exact_vacuum as vacuum
import s16_massless_tensor as tensor

def run_block(c,method,cache,freeze,fixed,deadline):
 begin=time.perf_counter();r=vacuum.reduce(c)
 if r is None:r=tensor.reduce(c)
 if r is None:r=formula(c)
 if r is not None:r['complete_seconds']=time.perf_counter()-begin;return r
 if len(c['definition']['propagators'])>31:return dict(success=False,status='unsupported_native_index_count',attempts=[],model_used=False)
 if not cache:cache.update(READ(HERE/'extension/basis_cache.json'))
 if method=='learned' and not freeze:freeze.update(READ(HERE/'extension/deployment/freeze.json'))
 if method=='fixed' and fixed is None:fixed=READ(HERE/'extension/deployment/fixed.json')['action']
 entry=cache['entries'].get(key(c));basis=restore_basis(c,entry['basis']) if entry else None
 action,scores=choose(c,freeze) if method=='learned' else (fixed if method=='fixed' else 'native',None)
 if basis is None and action in ['tight','dots','rank_minus','truncate_dots']:
  allowed=['native','rank_plus','expanded','truncate','truncate_rank_plus','truncate_relaxed'];action=min(allowed,key=lambda a:scores[ACTIONS.index(a)]) if scores is not None else 'native'
 attempts=[];seen=set()
 def call(a,basis,order=1):
  b=inputs.bounds(c,a);tr=inputs.truncation(c,a);signature=json.dumps([b,tr,basis,order],sort_keys=True)
  if signature in seen:return None
  seen.add(signature);left=deadline-time.perf_counter()
  if left<12:return dict(success=False,status='total_time_budget')
  with rt.environment():
   os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
   r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=min(45,left),margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=order,threads=1,truncate=tr)
  r=rt.compact(r);r['action']=a
  if r['success'] and basis is not None:
   allowed={label(a) for a in basis};used={m for row in r['coefficients'].values() for m in row}
   if not used<=allowed:r.update(success=False,status='outside_checked_master_basis',unexpected_masters=sorted(used-allowed))
  attempts.append(r);return r
 result=dict(success=False,status='not_started')
 for a in dict.fromkeys([action,'native','expanded']):
  r=call(a,basis)
  if r is not None:result=r
  if result['success'] and (basis is not None or nontrivial(result)):break
 checks=0
 if result['success'] and basis is None:
  basis=result['masters'];check=call('expanded',basis,2);ok=check is not None and check['success']
  if ok:ok,checks=equal(result['coefficients'],check['coefficients'])
  if not ok:result=dict(result,success=False,status='discovered_basis_not_verified')
 return dict(success=result['success'],status=result.get('status'),coefficients=result.get('coefficients',{}),masters=result.get('masters',[]),route='native_kira_block',model_used=method=='learned',first_action=action,scores=scores,cache_hit=entry is not None,attempts=attempts,coefficient_checks=checks,complete_seconds=time.perf_counter()-begin)

def run(case,method='learned'):
 assert method in ['native','fixed','learned'];c=canonical(case);begin=time.perf_counter();deadline=begin+110
 parts=split_blocks(c);cache={};freeze={} if method=='learned' else None;solved={};records=[]
 for part in parts:
  sub=part['case'];d=sub['definition'];identity=json.dumps([d['loop_momenta'],d['external_momenta'],d['propagators'],d['scalarproduct_rules'],d.get('invariants',[]),sub['targets']],sort_keys=True)
  duplicate=identity in solved
  if not duplicate:solved[identity]=run_block(sub,method,cache,freeze,None,deadline)
  records.append(dict(indices=part['indices'],loops=part['loops'],case=sub,result=solved[identity],reused=duplicate))
  if not solved[identity]['success']:break
 success=len(records)==len(parts) and all(x['result']['success'] for x in records)
 return dict(success=success,status='completed' if success else 'incomplete_block_reduction',case=c['id'],method=method,loops=len(c['definition']['loop_momenta']),blocks=records,component_count=len(parts),unique_native_blocks=sum(not b['reused'] and b['result'].get('route')=='native_kira_block' for b in records),model_used=any(b['result'].get('model_used',False) for b in records),failed_attempts=sum(sum(not a['success'] for a in b['result'].get('attempts',[])) for b in records if not b['reused']),complete_seconds=time.perf_counter()-begin,representation='Product of checked component master expansions; coefficients are recomputed at current parameters.')
