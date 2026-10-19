"""Select shared native reductions after exact analytic simplification."""
from s00_batch_common import *
from s01_triangle import reduce as triangle

def run(c,method='learned'):
 begin=time.perf_counter();f=previous.candidate;old_formula=f.formulas;old_legacy=f.legacy;patched=[];basis_patches=[]
 if method=='previous':return previous.run(c,'final')
 def formulas(c):
  if method=='previous_prepared':return old_formula(c)
  r=triangle(c)
  return old_formula(c) if r is None else r
 def patched_legacy():
  obj=old_legacy();p=obj.previous;original=p.run_block
  original_basis=obj.basis;basis_patches.append((obj,original_basis));obj.basis=lambda c:additional_basis(c,obj.h) or original_basis(c)
  def block(c,prior_method,cache,freeze,deadline):
   if method=='previous_prepared':return original(c,prior_method,cache,freeze,deadline)
   if method=='all_fixed':prior_method='fixed'
   if not eligible(c):return original(c,prior_method,cache,freeze,deadline)
   tick=time.perf_counter();action,scores=choose(c,method);decision=time.perf_counter()-tick
   if action=='prior':
    r=original(c,prior_method,cache,freeze,deadline);r.update(batch_action=action,batch_prediction_seconds=decision,batch_model_used=scores is not None,model_used=scores is not None or r.get('model_used',False));return r
   parts=[c['targets']]
   if action=='rank_groups':
    ranks=sorted({sum(max(-v,0) for v in t) for t in c['targets']});parts=[[t for t in c['targets'] if sum(max(-v,0) for v in t)==rank] for rank in ranks]
   elif action=='single_targets':parts=[[t] for t in c['targets']]
   records=[];theta=[2.5,0,0,1.25,0,1,-.25] if action=='sparse_wide' else [1,0,0,0,1,1,0]
   for index,targets in enumerate(parts):
    sub=dict(c,id=c['id']+'_partition'+str(index),targets=targets,size=len(targets))
    if action=='single_targets':r=original(sub,prior_method,cache,freeze,deadline)
    else:
     saved_eligible=p.eligible;saved_read=p.READ
     def config(path):
      if str(path).endswith('hybrid_experts/trained_model/sparse_fixed.json'):return dict(theta=theta,native_action='truncate_rank_plus')
      return saved_read(path)
     try:
      p.eligible=lambda c:True;p.READ=config
      r=original(sub,'sparse_fixed',cache,freeze,deadline)
     finally:p.eligible=saved_eligible;p.READ=saved_read
    records.append(r)
    if not r['success']:break
   success=len(records)==len(parts) and all(r['success'] for r in records)
   return dict(success=success,status='completed' if success else 'batch_reduction_incomplete',route='learned_shared_native',coefficients={t:row for r in records for t,row in r.get('coefficients',{}).items()},masters=[list(a) for a in sorted({tuple(a) for r in records for a in r.get('masters',[])})],attempts=[a for r in records for a in r.get('attempts',[])],model_used=scores is not None or any(r.get('model_used',False) for r in records),batch_model_used=scores is not None,batch_action=action,batch_prediction_seconds=decision,partitions=len(parts),scores=scores)
  patched.append((p,original));p.run_block=block;return obj
 try:
  f.formulas=formulas;f.legacy=patched_legacy;r=previous.run(c,'final')
  r.update(application='analytic_batch',batch_method=method,total_seconds=time.perf_counter()-begin);return r
 finally:
  f.formulas=old_formula;f.legacy=old_legacy
  for p,original in reversed(patched):p.run_block=original
  for obj,original in reversed(basis_patches):obj.basis=original

if __name__=='__main__':
 import argparse,traceback
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r)
