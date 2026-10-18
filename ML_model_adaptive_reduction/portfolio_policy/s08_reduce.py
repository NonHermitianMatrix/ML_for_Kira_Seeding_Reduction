"""Keep exact formulae, validation-selected ML choices, and previous fallbacks."""
from s00_common import *
def reduce(c,basis,reference=None):
 begin=time.perf_counter();c=dict(c);c.setdefault('group',c['id']);c.setdefault('split','application');c.setdefault('topology_group','unknown')
 n=len(c['definition']['propagators'])
 if c['size']!=len(c['targets']) or not c['targets'] or any(len(a)!=n or any(type(v) is not int for v in a) for a in c['targets']+basis):raise ValueError('Invalid integral indices')
 # The exact scalar formula does not require native sector or index storage.
 sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/massless_banana'))
 import s00_formula
 r=s00_formula.reduce(c,basis)
 if r is not None:
  if reference:rt.verify(r,reference)
  r.update(selection=dict(prediction_used=False,reason='exact_scalar_formula'),complete_seconds=time.perf_counter()-begin);return r
 cfg=read(HERE/'trained_model/fixed.json');entry=cfg['domains'].get(inputs.signature(c))
 if entry and entry['deploy']:
  learned=module('portfolio_seed',HERE/'s01_application.py').reduce
  r=learned(c,basis,'learned',reference);r['route']='validated_family_cost'
 else:
  sys.path.insert(0,str(ROOT/'ML_model_seed_selection/joint_policy'))
  import s05_application as previous
  r=previous.Reducer('learned',reuse=False).reduce({k:c[k] for k in ['id','size','definition','targets']},basis,reference)
  r['portfolio_fallback']=True
 r['complete_seconds']=time.perf_counter()-begin;return r
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 r=reduce(read(a.case),read(a.basis));write(a.output,r);print(json.dumps(dict(success=r['success'],route=r.get('route'),seconds=r['complete_seconds'])))
