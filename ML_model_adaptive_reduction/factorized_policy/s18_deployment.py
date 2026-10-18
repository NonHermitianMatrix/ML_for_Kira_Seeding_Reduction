"""Select the learned and fixed policies for work left after exact formulas."""
from s00_common import *
from s02_model import predict,choose
from s03_runtime import formula
import s07_exact_vacuum as vacuum
import s16_massless_tensor as tensor
DEST=HERE/'extension/deployment'

def main():
 rows=READ(HERE/'training/rows.json.gz')['validation'];native=[];exact=[]
 for r in rows:
  c=r['case'];out=vacuum.reduce(c)
  if out is None:out=tensor.reduce(c)
  if out is None:out=formula(c)
  (exact if out is not None else native).append(r)
 assert native
 totals=[sum(r['costs'][j] for r in native) for j in range(len(ACTIONS))];fixed=min(range(len(totals)),key=totals.__getitem__)
 legacy=READ(HERE/'trained_model/freeze.json');models={'previous_shared_model':legacy['model']}
 for p in (HERE/'trained_model').glob('*.json'):
  m=READ(p)
  if m.get('kind') in ['trees','ridge','mlp']:models[p.stem]=m
 options=[]
 for name,m in models.items():
  predictions=[predict(m,features(r['case'])) for r in native]
  for anchor in sorted({0,fixed}):
   for margin in [0.,.05,.15,.3]:
    ids=[min(range(len(ACTIONS)),key=row.__getitem__) if min(row)<row[anchor]-margin else anchor for row in predictions]
    cost=sum(r['costs'][j] for r,j in zip(native,ids));options.append(dict(candidate=name,anchor=anchor,margin=margin,cost_seconds=cost,ratio_native=cost/totals[0],ratio_fixed=cost/totals[fixed],changed_from_fixed=sum(j!=fixed for j in ids),first_failures=sum(r['first_failures'][j] for r,j in zip(native,ids))))
 best=min(options,key=lambda x:(x['cost_seconds'],x['changed_from_fixed']))
 legacy_cost=sum(r['costs'][ACTIONS.index(choose(r['case'],legacy)[0])] for r in native)
 selected=best if best['cost_seconds']<.99*legacy_cost else dict(legacy['selection'],candidate='previous_shared_model',cost_seconds=legacy_cost,ratio_native=legacy_cost/totals[0],ratio_fixed=legacy_cost/totals[fixed])
 freeze=dict(complete=True,model=models[selected['candidate']],selection=selected,validation_native_requests=len(native),validation_exact_requests=len(exact),legacy_validation_cost=legacy_cost,fixed_action=ACTIONS[fixed],fixed_validation_cost=totals[fixed],native_validation_cost=totals[0],changed_from_previous=selected['candidate']!='previous_shared_model' or selected['anchor']!=legacy['selection']['anchor'] or selected['margin']!=legacy['selection']['margin'],options=options,source_training_sha256=sha(HERE/'training/rows.json.gz'),scope='Historical validation only, restricted to requests that still need native Kira after exact formulas. No reserved result is used.')
 write(DEST/'freeze.json',freeze);write(DEST/'fixed.json',dict(action=ACTIONS[fixed]));summary={k:v for k,v in freeze.items() if k not in ['model','options']};summary['model_kind']=freeze['model']['kind'];write(DEST/'selection.json',summary);print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
