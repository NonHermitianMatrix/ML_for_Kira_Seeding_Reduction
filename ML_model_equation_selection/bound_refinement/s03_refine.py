"""Select filters by complete validation cost and test on new reserved physical inputs."""
import argparse,contextlib,json,statistics,time
from s00_probe import HERE,ROOT,BOUNDS,rt,inputs,attempt,save

def run(c,ref,option,action):
 start=time.perf_counter();basis=rt.read(ref)['masters'];weight=HERE/'trained_model'/(option['name']+'.txt') if option else None
 seq=[(action,weight,option['threshold'] if option else 0)]
 if weight:seq.append((action,None,0))
 seq.extend((a,None,0) for a in ['native','expanded'] if a!=action)
 attempts=[];seen=set()
 for a,w,t in seq:
  key=(tuple(inputs.bounds(c,a)),inputs.truncation(c,a),str(w),t)
  if key in seen:continue
  seen.add(key);r=attempt(c,basis,a,w,t);attempts.append(rt.compact(r))
  if r['success']:break
 out=dict(case=c['id'],graph=c['topology_group'],option=option,seed_action=action,success=r['success'],attempts=attempts,coefficients=r.get('coefficients',{}),fallbacks=len(attempts)-1,reference_coefficients_supplied=False)
 rt.verify(out,ref);out['complete_seconds']=time.perf_counter()-start;return out

def validate():
 import s10_fit_graph
 s10_fit_graph.main()
 import s14_check_union
 s14_check_union.main()
 import s13_seed_filter
 s13_seed_filter.main()
 import s11_parity
 s11_parity.main()
 cfg=rt.read(BOUNDS/'trained_model/fixed.json');candidates=rt.read(HERE/'trained_model/candidates.json');cases=rt.read(BOUNDS/'protocol.json')['splits']['validation'];results={}
 for c in cases:
  if not (HERE/'validation'/(c['id']+'.json.gz')).exists():continue
  graph=c['topology_group'];opts=[None]+candidates['candidates'].get(graph,[]);ref=BOUNDS/'references'/(c['id']+'.json.gz')
  for j in range(3):
   for k in [(n+j)%len(opts) for n in range(len(opts))]:
    p=HERE/'validation_cost'/(c['id']+f'_o{k}_r{j}.json.gz')
    if p.exists():continue
    r=run(c,ref,opts[k],cfg['fixed_by_graph'][graph]);save(p,r)
    print(json.dumps(dict(stage='validation',case=c['id'],option=k,repetition=j,seconds=r['complete_seconds'],success=r['success'],fallbacks=r['fallbacks'])),flush=True)
 for graph,options in candidates['candidates'].items():
  cs=[c for c in cases if c['topology_group']==graph and (HERE/'validation'/(c['id']+'.json.gz')).exists()];times=[]
  for k in range(len(options)+1):
   records=[[rt.read(HERE/'validation_cost'/(c['id']+f'_o{k}_r{j}.json.gz')) for j in range(3)] for c in cs]
   times.append(sum(statistics.median(r['complete_seconds'] for r in rs) for rs in records) if records and all(r['success'] for rs in records for r in rs) else None)
  best=min([i for i,v in enumerate(times) if v is not None],key=lambda i:times[i]) if any(v is not None for v in times) else 0
  selected=options[best-1] if best and times[best]<.95*times[0] else None
  results[graph]=dict(option=selected,seconds=times,validation_cases=[c['id'] for c in cs],minimum_relative_gain=.05)
 freeze=dict(complete=True,selection=results,seed_config=cfg,models={str(p.relative_to(HERE)):inputs.sha(p) for p in (HERE/'trained_model').glob('*.txt')},source_hashes={p.name:inputs.sha(p) for p in [HERE/'s00_probe.py',HERE/'s02_train.py',HERE/'s03_refine.py',HERE/'s10_fit_graph.py',HERE/'s11_parity.py',HERE/'s07_reduce.py',HERE/'s12_application.py',HERE/'s13_seed_filter.py',HERE/'s14_check_union.py']},features=rt.read(BOUNDS/'trained_model/freeze.json')['domain'],source_protocol=inputs.sha(BOUNDS/'protocol.json'),test_profiles=[525,526],test_repetitions=5,controls='Same fixed seed setting, exact code, and basis; all ML disabled.',frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
 inputs.write(HERE/'trained_model/freeze.json',freeze);print(json.dumps(dict(stage='frozen',selection=results)),flush=True)

def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz');q=HERE/'references'/(c['id']+'_check.json.gz')
 if p.exists() and q.exists():
  return p if rt.read(p)['success'] and rt.read(q)['success'] and rt.read(q).get('reference_checked') else None
 if p.exists():r=rt.read(p)
 else:r=rt.attempt(c,action='expanded',timeout=120);save(p,rt.compact(r))
 if not r['success']:return None
 if q.exists():check=rt.read(q)
 else:
  b=inputs.bounds(c,'expanded');b[1]+=1;check=rt.attempt(c,basis=r['masters'],custom=b,timeout=120);rt.verify(check,p);save(q,rt.compact(check))
 return p if check['success'] else None

def test():
 freeze=rt.read(HERE/'trained_model/freeze.json');assert freeze['complete']
 for name,h in freeze['source_hashes'].items():assert inputs.sha(HERE/name)==h
 for name,h in freeze['models'].items():assert inputs.sha(HERE/name)==h
 cases=[]
 old=rt.read(BOUNDS/'protocol.json')['splits']['validation']
 for h in freeze['test_profiles']:
  cases.extend(inputs.case(c['topology_group'],h,c['shape'],'reserved') for c in old)
 protocol=dict(cases=cases,freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'),repetitions=freeze['test_repetitions'],methods=['off','learned'])
 p=HERE/'model_test/protocol.json'
 if p.exists():assert rt.read(p)==protocol
 else:inputs.write(p,protocol)
 for c in cases:
  ref=reference(c)
  if ref is None:
   inputs.write(HERE/'model_test'/(c['id']+'_excluded.json'),dict(case=c['id'],reason='Reference or expanded check failed within resource bounds.'));continue
  graph=c['topology_group'];entry=freeze['selection'].get(graph,dict(option=None));option=entry['option'];action=freeze['seed_config']['fixed_by_graph'][graph]
  for j in range(freeze['test_repetitions']):
   for method in (['off','learned'] if j%2==0 else ['learned','off']):
    p=HERE/'model_test'/(c['id']+'_'+method+f'_r{j}.json.gz')
    if p.exists():continue
    # Include policy loading and domain checks. Reference coefficient loading is the common exact comparison only.
    start=time.perf_counter();f=rt.read(HERE/'trained_model/freeze.json') if method=='learned' else None
    use=option if method=='learned' else None
    if use:
     domain=f['features'].get(graph);x=inputs.features(c)
     if domain is None or inputs.signature(c) not in domain['signatures'] or any(x[i]<domain['minimum'][i]-1e-9 or x[i]>domain['maximum'][i]+1e-9 for i in [5,6,7,21,25]):use=None
    r=run(c,ref,use,action);r.update(method=method,policy_load_and_guard_seconds=time.perf_counter()-start-r['complete_seconds']);r['complete_seconds']=time.perf_counter()-start
    save(p,r);print(json.dumps(dict(stage='reserved',case=c['id'],method=method,repetition=j,seconds=r['complete_seconds'],success=r['success'],fallbacks=r['fallbacks'],model=None if use is None else use['name'])),flush=True)
 inputs.write(HERE/'model_test/completion.json',dict(complete=True,freeze_sha256=protocol['freeze_sha256']))

def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['validate','test','all']);a=p.parse_args()
 if a.stage in ['validate','all']:validate()
 if a.stage in ['test','all']:test()
if __name__=='__main__':main()
