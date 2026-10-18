"""Public application with optional master basis and exact scalar shortcuts."""
from s00_common import *
import s11_reduce as supplied
import s20_prepare_resilient as prepared

def reduce(case,basis=None,mode='auto'):
 begin=time.perf_counter()
 if mode not in ['auto','learned','native']:raise ValueError('Unsupported method')
 if basis is not None:return supplied.reduce(case,basis,mode=mode)
 d=case['definition'];n=d['physical_propagators'];N=len(d['propagators'])
 proposed=[[1]*n+[0]*(N-n)]
 formula=module('optional_basis_scalar',ROOT/'ML_model_adaptive_reduction/massless_banana/s00_formula.py')
 result=formula.reduce(case,proposed)
 if result is not None:
  result.update(route='exact_scalar_formula',model_used=False,complete_seconds=time.perf_counter()-begin);return result
 if mode=='auto':mode=READ(HERE/'preparation/deployment.json')['preparation_method']
 result=prepared.run(case,'cached_learned' if mode=='learned' else 'cached_native')
 result.update(route='prepared_shared_model' if mode=='learned' else 'prepared_native',model_used=mode=='learned' and result.get('status')!='unsupported_native_index_count',complete_seconds=time.perf_counter()-begin)
 return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis');p.add_argument('--output',required=True);p.add_argument('--method',default='auto',choices=['auto','learned','native']);a=p.parse_args()
 result=reduce(READ(a.case),READ(a.basis) if a.basis else None,a.method);write(a.output,result)
 print(json.dumps(dict(success=result['success'],route=result['route'],seconds=result['complete_seconds'])))
