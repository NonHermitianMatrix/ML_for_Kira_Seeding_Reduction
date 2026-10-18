"""Reduce independent loop blocks with exact formulas or ML-guided native Kira."""
from s00_common import *
from s01_families import split_blocks
from s02_model import choose

def formula(c):
 d=c['definition'];P=d['physical_propagators'];N=len(d['propagators'])
 if len(d['loop_momenta'])==1 and not d['external_momenta'] and P==N==1:
  m=d['propagators'][0]['mass_squared']
  if m=='0':return dict(success=True,coefficients={label(t):{} for t in c['targets']},masters=[],route='scaleless_tadpole',model_used=False,attempts=[])
  rows={}
  for t in c['targets']:
   a=t[0]
   rows[label(t)]={} if a<=0 else {'1':'*'.join('(d-'+str(2*j)+')/('+str(2*j)+'*('+m+'))' for j in range(1,a)) or '1'}
  return dict(success=True,coefficients=rows,masters=[[1]],route='tadpole_recurrence',model_used=False,attempts=[])
 if not d['external_momenta'] or any(p['mass_squared']!='0' for p in d['propagators'][:P]) or any(any(a!=0 for a in t[P:]) for t in c['targets']):return None
 f=module('factor_scalar_formula',ROOT/'ML_model_adaptive_reduction/massless_banana/s00_formula.py')
 r=f.reduce(c,[[1]*P+[0]*(N-P)])
 if r is not None:r.update(route='massless_scalar_recurrence',model_used=False,attempts=[])
 return r

def run_block(c,method,cache,freeze,fixed,deadline,allow_formulas=True):
 begin=time.perf_counter()
 r=formula(c) if allow_formulas else None
 if r is not None:r['complete_seconds']=time.perf_counter()-begin;return r
 if len(c['definition']['propagators'])>31:return dict(success=False,status='unsupported_native_index_count',attempts=[],model_used=False)
 if not cache:cache.update(READ(HERE/'basis_cache.json'))
 if method=='learned' and not freeze:freeze.update(READ(HERE/'trained_model/freeze.json'))
 if method=='fixed' and fixed is None:fixed=READ(HERE/'trained_model/fixed.json')['action']
 entry=cache['entries'].get(key(c));basis=restore_basis(c,entry['basis']) if entry else None
 action,scores=choose(c,freeze) if method=='learned' else (fixed if method=='fixed' else 'native',None)
 if basis is None and action in ['tight','dots','rank_minus','truncate_dots']:
  permitted=['native','rank_plus','expanded','truncate','truncate_rank_plus','truncate_relaxed']
  action=min(permitted,key=lambda a:scores[ACTIONS.index(a)]) if scores is not None else 'native'
 attempts=[];seen=set();initial_basis=basis
 def call(action,basis,ordering=1):
  b=inputs.bounds(c,action);tr=inputs.truncation(c,action);sig=json.dumps([b,tr,basis,ordering],sort_keys=True)
  if sig in seen:return None
  seen.add(sig);left=deadline-time.perf_counter()
  if left<12:return dict(success=False,status='total_time_budget')
  with rt.environment():
   os.environ['KIRA_RUNTIME_BINARY']=str(ROOT/'.tools/kira-sector-wide/kira');os.environ['KIRA_BOUNDED_SECTOR_ARRAYS']='1'
   r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=min(45,left),margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=b,ordering=ordering,threads=1,truncate=tr)
  r=rt.compact(r);r['action']=action;attempts.append(r);return r
 result=dict(success=False,status='not_started')
 for a in dict.fromkeys([action,'native','expanded']):
  r=call(a,basis)
  if r is not None:result=r
  if result['success'] and (basis is not None or nontrivial(result)):break
 refreshed=False
 if not result['success'] and basis is not None:
  refreshed=True;basis=None;r=call('expanded',None)
  if r is not None:result=r
 checks=0
 if result['success'] and basis is None:
  basis=result['masters'];check=call('expanded',basis,2)
  valid=check is not None and check['success']
  if valid:valid,checks=equal(result['coefficients'],check['coefficients'])
  if not valid:result=dict(result,success=False,status='discovered_basis_not_verified')
 return dict(success=result['success'],status=result.get('status'),coefficients=result.get('coefficients',{}),masters=result.get('masters',[]),route='native_kira_block',model_used=method=='learned',first_action=action,scores=scores,cache_hit=initial_basis is not None,basis_refreshed=refreshed,attempts=attempts,coefficient_checks=checks,complete_seconds=time.perf_counter()-begin)

def run(c,method='learned',allow_formulas=True):
 if method not in ['native','fixed','learned']:raise ValueError(method)
 begin=time.perf_counter();deadline=begin+110;parts=split_blocks(c)
 cache={};freeze={} if method=='learned' else None;fixed=None
 solved={};records=[]
 for part in parts:
  sub=part['case'];identity=json.dumps([sub['definition'],sub['targets']],sort_keys=True)
  # IDs and block positions never enter the exact within-request reuse key.
  identity=json.dumps([sub['definition']['loop_momenta'],sub['definition']['external_momenta'],sub['definition']['propagators'],sub['definition']['scalarproduct_rules'],sub['definition'].get('invariants',[]),sub['targets']],sort_keys=True)
  duplicate=identity in solved
  if not duplicate:solved[identity]=run_block(sub,method,cache,freeze,fixed,deadline,allow_formulas)
  records.append(dict(indices=part['indices'],loops=part['loops'],case=sub,result=solved[identity],reused=duplicate))
  if not solved[identity]['success']:break
 success=len(records)==len(parts) and all(x['result']['success'] for x in records)
 return dict(success=success,status='completed' if success else 'incomplete_block_reduction',case=c['id'],method=method,loops=len(c['definition']['loop_momenta']),blocks=records,component_count=len(parts),unique_native_blocks=sum(not x['reused'] and x['result'].get('route')=='native_kira_block' for x in records),model_used=any(x['result'].get('model_used',False) for x in records),failed_attempts=sum(sum(not a['success'] for a in x['result'].get('attempts',[])) for x in records if not x['reused']),complete_seconds=time.perf_counter()-begin,representation='Product of exact component reductions; no exponential expansion of the product master basis.')

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned',choices=['native','fixed','learned']);a=p.parse_args()
 try:r=run(READ(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-2500:])
 write(a.output,r);print(json.dumps(dict(success=r['success'],status=r['status'])))
