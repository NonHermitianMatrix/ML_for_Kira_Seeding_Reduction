"""Combine exact blocks, the complete-time baseline, and a trained sparse expert."""
from s00_cost_common import *
import tempfile,resource
choose=inputs.module('hybrid_cost_selector',HERE/'s03_train.py').choose

def run_block(c,method,cache,freeze,deadline):
 begin=time.perf_counter();r=exact(c)
 if r is not None:r['complete_seconds']=time.perf_counter()-begin;return r
 if len(c['definition']['propagators'])>31:return dict(success=False,status='unsupported_native_index_count',attempts=[],model_used=False)
 if not cache:cache.update(READ(BLOCK/'extension/basis_cache.json'))
 basis=basis_for(c,cache);supported=eligible(c);decision_start=time.perf_counter();scores=None
 if method=='learned' and supported and basis is not None:
  if not freeze:freeze.update(READ(HERE/'trained_model/freeze.json'))
  action,scores=choose(c,basis,freeze)
 elif method=='fixed' and supported:action=READ(HERE/'trained_model/fixed.json')['action']
 else:action=method if method in ACTIONS else 'base'
 if not supported and action.startswith('sparse_'):action='base'
 if basis is None:action='raw_native'
 decision_seconds=time.perf_counter()-decision_start;attempts=[];seen=set();inner_used=False;inner_scores=None
 base_action=READ(BASE/'trained_model/fixed.json')['action']
 # Preserve the measured expert actions. Outside that domain, do not extend
 # a fixed setting beyond the structural ranges used to select it.
 range_fallback=False
 if not supported and basis is not None:
  base_model=READ(BASE/'trained_model/freeze.json');x=features(c,basis)
  range_fallback=any(x[j]<base_model['minimum'][j]-1e-9 or x[j]>base_model['maximum'][j]+1e-9 for j in base_model['guard_features'])
  if range_fallback:base_action='raw_native'
 def call(a,basis,order=1):
  nonlocal inner_used,inner_scores,decision_seconds
  sparse=a.startswith('sparse_');theta=None
  if sparse:
   tick=time.perf_counter();config=READ(HERE/'trained_model/sparse_fixed.json')
   if a=='sparse_learned':theta,inner_scores=expert_theta(c);inner_used=True
   else:theta=config['theta']
   bounds=inputs.bounds(c,config['native_action']);truncation=inputs.truncation(c,config['native_action'])
   decision_seconds+=time.perf_counter()-tick
  else:bounds,truncation=settings(c,base_action if a=='base' else a,basis)
  signature=json.dumps([bounds,truncation,basis,order,theta],sort_keys=True)
  if signature in seen:return None
  seen.add(signature);left=deadline-time.perf_counter()
  if left<12:return dict(success=False,status='hybrid_budget')
  with tempfile.TemporaryDirectory(prefix='hybrid_seed_',dir=os.environ['TMPDIR']) as temporary:
   with rt.environment():
    os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
    seed_info=None
    if theta is not None:
     tick=time.perf_counter()
     try:
      selected,seed_info=geometry.seeds(c,basis,bounds,theta,truncation)
      payload=''.join('F['+','.join(map(str,v))+']\n' for v in selected)
      if len(payload.encode())>4*1024**2:raise ValueError('Sparse seed input exceeds 4 MiB')
      seed_path=Path(temporary)/'seeds.txt';seed_path.write_text(payload)
      os.environ['KIRA_ML_SEEDS']=str(seed_path)
      if os.environ.get('HYBRID_SEED_AUDIT')=='1':os.environ['KIRA_ML_SEED_AUDIT']=str(Path(temporary)/'audit.json')
      seed_info['preparation_seconds']=time.perf_counter()-tick
     except (ValueError,AssertionError) as error:
      r=dict(success=False,status='sparse_preparation_failed',error=str(error),action=a,native_called=False)
      attempts.append(r);return r
    left=deadline-time.perf_counter()
    if left<12:return dict(success=False,status='hybrid_budget')
    old_limit=resource.getrlimit(resource.RLIMIT_FSIZE)
    audit_mode=os.environ.get('HYBRID_SEED_AUDIT')=='1' and theta is not None
    if audit_mode:resource.setrlimit(resource.RLIMIT_FSIZE,(min(8*1024**2,old_limit[0]) if old_limit[0]>=0 else 8*1024**2,old_limit[1]))
    try:
     r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=min(45,left),margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=bounds,ordering=order,threads=1,truncate=truncation)
    finally:
     if audit_mode:resource.setrlimit(resource.RLIMIT_FSIZE,old_limit)
    r=rt.compact(r);r.update(action=a,native_called=True,seed_policy=seed_info)
    audit=Path(temporary)/'audit.json'
    if theta is not None and audit.exists():r['seed_audit']={k:v for k,v in json.loads(audit.read_text()).items() if k!='used'}
  if r['success'] and basis is not None:
   allowed={label(m) for m in basis};used={m for row in r['coefficients'].values() for m in row}
   if not used<=allowed:r.update(success=False,status='outside_checked_master_basis',unexpected_masters=sorted(used-allowed))
  attempts.append(r);return r
 result=dict(success=False,status='not_started')
 for a in dict.fromkeys([action,'base','native','expanded']):
  r=call(a,basis)
  if r is not None:result=r
  if result['success'] and (basis is not None or nontrivial(result)):break
 checks=0
 if result['success'] and basis is None:
  basis=result['masters'];check=call('expanded',basis,2);ok=check is not None and check['success']
  if ok:ok,checks=equal(result['coefficients'],check['coefficients'])
  if not ok:result=dict(result,success=False,status='discovered_basis_not_verified')
 return dict(success=result['success'],status=result.get('status'),coefficients=result.get('coefficients',{}),masters=result.get('masters',[]),route='native_kira_block',model_used=scores is not None or inner_used,outer_model_used=scores is not None,expert_model_used=inner_used,decision_seconds=decision_seconds,first_action=action,scores=scores,expert_scores=inner_scores,eligible=supported,range_fallback=range_fallback,attempts=attempts,coefficient_checks=checks,complete_seconds=time.perf_counter()-begin)

def run(case,method='learned'):
 assert method in ACTIONS+['fixed','learned'];c=canonical(case);begin=time.perf_counter();deadline=begin+110
 parts=split_blocks(c);cache={};freeze={};solved={};records=[]
 for part in parts:
  sub=part['case'];d=sub['definition'];identity=json.dumps([d['loop_momenta'],d['external_momenta'],d['propagators'],d['scalarproduct_rules'],d.get('invariants',[]),sub['targets']],sort_keys=True)
  duplicate=identity in solved
  if not duplicate:solved[identity]=run_block(sub,method,cache,freeze,deadline)
  records.append(dict(indices=part['indices'],loops=part['loops'],case=sub,result=solved[identity],reused=duplicate))
  if not solved[identity]['success']:break
 success=len(records)==len(parts) and all(b['result']['success'] for b in records)
 return dict(success=success,status='completed' if success else 'incomplete_block_reduction',case=c['id'],method=method,loops=len(c['definition']['loop_momenta']),blocks=records,component_count=len(parts),unique_native_blocks=sum(not b['reused'] and b['result'].get('route')=='native_kira_block' for b in records),model_used=any(b['result'].get('model_used',False) for b in records),failed_attempts=sum(sum(not a['success'] for a in b['result'].get('attempts',[])) for b in records if not b['reused']),complete_seconds=time.perf_counter()-begin,representation='Product of checked component master expansions; no cross-request coefficient reuse.')

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned');a=p.parse_args()
 try:r=run(READ(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1600:])
 write(a.output,r)
