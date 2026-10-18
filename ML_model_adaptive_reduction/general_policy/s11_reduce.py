"""Public reduction: exact scalar formula, otherwise the frozen shared policy."""
from s00_common import *
import s02_application as shared
shared.HERE=HERE/'refit'

def reduce(case,basis,reference=None,mode='auto'):
 begin=time.perf_counter()
 if mode not in ['auto','learned','native','fixed']:raise ValueError('Invalid method')
 formula=module('general_scalar_formula',ROOT/'ML_model_adaptive_reduction/massless_banana/s00_formula.py')
 result=formula.reduce(case,basis)
 if result is not None:
  if reference:rt.verify(result,reference)
  result.update(route='exact_scalar_formula',model_used=False,complete_seconds=time.perf_counter()-begin);return result
 if mode=='auto':mode='learned' if READ(HERE/'refit/trained_model/selection.json')['replace_default'] else 'native'
 result=shared.reduce(case,basis,mode,reference);result.update(route='shared_cost_model' if mode=='learned' else mode,model_used=bool(result.get('selection')),complete_seconds=time.perf_counter()-begin);return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='auto',choices=['auto','learned','native','fixed']);a=p.parse_args()
 r=reduce(READ(a.case),READ(a.basis),mode=a.method);write(a.output,r);print(json.dumps(dict(success=r['success'],route=r['route'],seconds=r['complete_seconds'])))
