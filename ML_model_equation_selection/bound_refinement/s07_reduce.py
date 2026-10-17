"""Reduce a target batch with a frozen learned equation filter and an exact master basis."""
import argparse,json,time
from pathlib import Path
from s00_probe import HERE,rt,inputs,attempt,save

def reduce(c,basis,method='learned'):
 start=time.perf_counter();n=len(c['definition']['propagators'])
 if not 0<n<=31 or c['size']!=len(c['targets']) or not c['targets']:raise ValueError('Unsupported target definition')
 if c['definition'].get('cut_propagators') or c['definition'].get('symbolic_ibp'):raise ValueError('Unsupported integral family')
 tops=c['definition']['top_level_sectors']
 if not tops or any(type(s) is not int or not 0<s<2**n for s in tops):raise ValueError('Invalid top sector')
 for a in c['targets']+basis:
  if len(a)!=n or any(type(v) is not int for v in a):raise ValueError('Invalid integral index vector')
  sector=sum(1<<i for i,v in enumerate(a) if v>0)
  if not any(sector&top==sector for top in tops):raise ValueError('Integral lies outside declared sectors')
 f=rt.read(HERE/'trained_model/freeze.json');matches=[g for g,v in f['features'].items() if inputs.signature(c) in v['signatures']];graph=matches[0] if len(matches)==1 else None
 option=None;action='native'
 if graph:
  action=f['seed_config']['fixed_by_graph'][graph];domain=f['features'][graph];x=inputs.features(c)
  if method=='learned' and all(domain['minimum'][i]-1e-9<=x[i]<=domain['maximum'][i]+1e-9 for i in [5,6,7,21,25]):option=f['selection'].get(graph,{}).get('option')
 weight=HERE/'trained_model'/(option['name']+'.txt') if option else None
 if weight:assert inputs.sha(weight)==f['models'][str(weight.relative_to(HERE))]
 loaded=time.perf_counter()-start;seq=[(action,weight,option['threshold'] if option else 0)]
 if weight:seq.append((action,None,0))
 seq.extend((a,None,0) for a in ['native','expanded'] if a!=action);seen=set();attempts=[]
 for a,w,t in seq:
  key=(tuple(inputs.bounds(c,a)),inputs.truncation(c,a),str(w),t)
  if key in seen:continue
  seen.add(key);r=attempt(c,basis,a,w,t);attempts.append(rt.compact(r))
  if r['success']:break
 return dict(case=c['id'],method=method,graph=graph,option=option,seed_action=action,success=r['success'],coefficients=r.get('coefficients',{}),attempts=attempts,fallbacks=len(attempts)-1,policy_loading_and_selection_seconds=loaded,complete_seconds=time.perf_counter()-start,reference_coefficients_supplied=False,basis_supplied=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--basis',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--method',choices=['learned','off'],default='learned');a=p.parse_args()
 r=reduce(rt.read(a.case),rt.read(a.basis),a.method);save(a.output,r);print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],filter=r['option'])),flush=True)
if __name__=='__main__':main()
