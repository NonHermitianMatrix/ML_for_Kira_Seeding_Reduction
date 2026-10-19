"""Use direct exact formulas, a learned recurrence choice, and native Kira fallback."""
from s00_fast_common import *
from s01_fast_recurrence import reduce as recurrence
from s02_fast_formulas import reduce as formulas

def recurrence_features(c):
 d=c['definition'];ts=c['targets'];N=len(d['propagators']);dots=[sum(max(v-1,0) for v in a) for a in ts]
 return [N,len(ts),max(dots),sum(dots)/len(ts),max(max(a) for a in ts),min(sum(v>0 for v in a) for a in ts)]+[max((a[j] for a in ts),default=0) if j<N else 0 for j in range(5)]

def choose(c,method):
 p=HERE/'trained_model/recurrence.json'
 if not p.exists():return 'largest',False
 f=read(p)
 if method=='fixed' or not f['enabled']:return f['fixed'],False
 x=recurrence_features(c)
 if any(x[j]<f['minimum'][j] or x[j]>f['maximum'][j] for j in range(len(x))):return f['fixed'],False
 costs=[]
 for t in f['trees']:
  while 'feature' in t:t=t['left'] if x[t['feature']]<=t['cut'] else t['right']
  costs.append(t['cost'])
 values=[sum(a[i] for a in costs)/len(costs) for i in range(4)];idx=min(range(4),key=values.__getitem__);fixed=f['actions'].index(f['fixed'])
 if values[idx]+f['allowance']>=values[fixed]*(1-f['margin']):idx=fixed
 return f['actions'][idx],True

def run(case,method='learned'):
 assert method in ['learned','fixed'];begin=time.perf_counter();deadline=begin+110;c=canonical(case);parts=split_blocks(c);memo={};records=[];old=None;cache={};freeze={}
 for part in parts:
  sub=part['case'];d=sub['definition'];key=json.dumps([d['loop_momenta'],d['external_momenta'],d['propagators'],d['scalarproduct_rules'],d.get('invariants',[]),sub['targets']],sort_keys=True);duplicate=key in memo
  if not duplicate:
   start=time.perf_counter();r=formulas(sub);used=False
   if r is None:
    pivot,used=choose(sub,method) if len(d['loop_momenta'])==1 and len(d['propagators'])<=5 else ('largest',False)
    r=recurrence(sub,deadline=min(deadline,time.perf_counter()+5),pivot=pivot,backend='gmp')
    if r is not None:r=admit(sub,r)
    if r is not None:r.update(model_used=used,pivot=pivot)
   if r is None:
    if old is None:old=legacy()
    # Preserve prior exact methods and native/model fallback for other structures.
    saved_exact=old.previous.exact;saved_basis=old.previous.basis_for
    try:
     old.previous.exact=old.admitted_exact;old.previous.basis_for=lambda c,cache:old.basis(c)
     r=old.previous.run_block(sub,'learned' if method=='learned' else 'fixed',cache,freeze,deadline)
    finally:old.previous.exact=saved_exact;old.previous.basis_for=saved_basis
   r['block_total_seconds']=time.perf_counter()-start;memo[key]=r
  records.append(dict(indices=part['indices'],loops=part['loops'],case=sub,result=memo[key],reused=duplicate))
  if not memo[key]['success']:break
 ok=len(records)==len(parts) and all(b['result']['success'] for b in records)
 return dict(success=ok,status='completed' if ok else 'incomplete_block_reduction',case=c['id'],method=method,loops=len(c['definition']['loop_momenta']),blocks=records,component_count=len(parts),model_used=any(b['result'].get('model_used',False) for b in records),complete_seconds=time.perf_counter()-begin,representation='Product of independently reduced loop blocks.')

if __name__=='__main__':
 import argparse,traceback
 os.environ['SYMPY_GROUND_TYPES']='python'
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned');a=p.parse_args()
 try:r=run(read(a.case),a.method)
 except Exception as e:r=dict(success=False,status='exception',error=repr(e),traceback=traceback.format_exc()[-1400:])
 write(a.output,r);print(json.dumps(dict(success=r['success'],status=r['status'])))
