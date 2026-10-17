"""Use the new seed model inside the existing exact reduction workflow."""
import argparse,gzip,json,sys,time
from s05_reduce import reduce as sparse_reduce,choose
from s00_policy import HERE,ROOT,rt,inputs

def supports(c):
 d=c['definition']
 if len(d['loop_momenta'])!=2 or d['physical_propagators']!=7 or len(d['propagators'])!=9 or len(c['targets'])!=1:return False
 for p in sorted((HERE/'trained_model').glob('cost_*.json')):
  f=rt.read(p)
  if inputs.signature(c)!=f['signature']:continue
  # Check the input domain without running a predictor twice.
  theta,info=choose(c,f,'fixed')
  if info['reason']!='frozen_policy':return False
  # Eligibility uses validation costs only; no reserved result is consulted.
  v=rt.read(HERE/'cost_validation'/(f['graph']+'_selection.json'));cost=v['costs']
  selected=sum(row[j] for row,j in zip(cost,f['validation_choices'])) if f['enabled'] else sum(row[f['fixed_index']] for row in cost)
  return selected<.97*sum(row[0] for row in cost)
 return False

def reduce(c,basis=None,previous=False):
 start=time.perf_counter()
 sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/massless_banana'))
 from s00_formula import reduce as analytic
 r=analytic(c,basis)
 if r is not None:r['route']='proven_massless_banana'
 elif not previous and supports(c):
  if basis is None:raise ValueError('Native reduction requires a supplied basis')
  r=sparse_reduce(c,basis);r['route']='cost_trained_sparse_seeds'
 else:
  if basis is None:raise ValueError('Native reduction requires a supplied basis')
  sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/batch_policy'))
  from s16_deployment import reduce as old_reduce
  r=old_reduce(c,basis,'learned');r['route']='native_kira_with_batch_policy'
 r['complete_seconds']=time.perf_counter()-start;return r

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis');p.add_argument('--output',required=True);p.add_argument('--previous',action='store_true');a=p.parse_args()
 from pathlib import Path
 r=reduce(rt.read(a.case),rt.read(a.basis) if a.basis else None,a.previous)
 raw=json.dumps(r,separators=(',',':')).encode();assert len(raw)<2*1024**2
 Path(a.output).write_bytes(gzip.compress(raw,mtime=0) if a.output.endswith('.gz') else raw)
 print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],route=r['route'])))
