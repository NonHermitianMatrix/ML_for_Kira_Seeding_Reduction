"""Use a proven analytic specialization, then the trained native Kira workflow."""
import argparse,gzip,json,sys,time
from pathlib import Path
from s00_formula import reduce as analytic
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def reduce(case,basis=None,strategy='learned'):
 start=time.perf_counter();r=analytic(case,basis)
 if r is None:
  if basis is None:raise ValueError('The native ML interface requires a supplied master basis.')
  sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/batch_policy'))
  from s16_deployment import reduce as native
  r=native(case,basis,strategy);r['route']='native_kira_with_batch_policy'
 else:r['route']='proven_massless_banana'
 r['complete_seconds']=time.perf_counter()-start;return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis');p.add_argument('--output',required=True);p.add_argument('--strategy',choices=['learned','fixed_off','previous','off'],default='learned');a=p.parse_args()
 c=json.loads(Path(a.case).read_text());basis=json.loads(Path(a.basis).read_text()) if a.basis else None;r=reduce(c,basis,a.strategy);raw=json.dumps(r,separators=(',',':')).encode();assert len(raw)<2*1024**2
 Path(a.output).write_bytes(gzip.compress(raw,mtime=0) if a.output.endswith('.gz') else raw)
 print(json.dumps(dict(success=r['success'],route=r['route'],seconds=r['complete_seconds'])))
