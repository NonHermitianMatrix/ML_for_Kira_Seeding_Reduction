"""Train graph-specific cost models, freeze validation choices, and test once."""
import argparse,copy,hashlib,json,math,statistics,time
import s00_study as st
import s03_truncate as tr
from pathlib import Path

BASE=['native','sector','truncate0','truncate1','sector_truncate0','tight','equation','expanded','order5']
SHAPES=['top','pinch','numerator']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def attempt(c,ref,config,margin=0,basis=None):
 if config=='sector_truncate0':
  cc=copy.deepcopy(c);cc['definition']['top_level_sectors']=st.sectors(c)
  return tr.adapted(cc,ref,'truncate0',margin,basis)
 return tr.adapted(c,ref,config,margin,basis)
st.attempt=attempt
def canonical(c,cfg):
 if cfg=='tight' and st.seed_bounds(c,'tight')[1]==st.seed_bounds(c,'native')[1]:return 'native'
 if st.sectors(c)==c['definition']['top_level_sectors']:
  return {'sector':'native','sector_truncate0':'truncate0'}.get(cfg,cfg)
 return cfg
def prepare():
 candidates=[st.make_case(k,h,s,split) for split,hs in [('training',[62,63]),('validation',[64]),('reserved',[65,66])]
        for h in hs for k in st.KINDS for s in SHAPES]
 cases=[];seen=set()
 for c in candidates:
  key=(c['group'],tuple(map(tuple,c['targets'])))
  if key not in seen:cases.append(c);seen.add(key)
 protocol=dict(cases=cases,configurations=BASE,training_repetitions=2,validation_repetitions=3,test_repetitions=5,
  positive_bound_floor='Before each attempt, r is at least the largest positive-index count of the declared top-level sectors.',
  test_methods=['native','deterministic','family_fixed','learned'],minimum_validation_gain=.05,
  selection='Minimize full validation time separately within each known graph. Enable a model only if validation saves at least five percent against the fastest control.',
  scope='Seven known graph structures at fresh rational profiles. The dimension remains symbolic. Training and test target shapes overlap; kinematic profiles do not.')
 p=st.HERE/'protocol.json'
 if p.exists():assert json.loads(p.read_text())==protocol
 else:st.write(p,protocol)
 for d in ['training','validation','trained_model','model_test']:(st.HERE/d).mkdir(exist_ok=True)
 return cases
def measure(cases,split,reps):
 for c in cases:
  if c['split']!=split:continue
  ref=st.reference(c)
  configs=list(dict.fromkeys(canonical(c,cfg) for cfg in BASE))
  for rep in range(reps):
   order=configs[rep%len(configs):]+configs[:rep%len(configs)]
   if rep%2:order.reverse()
   for cfg in order:
    p=st.HERE/split/f'{c["id"]}_{cfg}_{rep}.json.gz'
    if p.exists():continue
    r=st.workflow(c,ref,cfg);r['repetition']=rep;st.save(p,r)
    st.emit(stage=split,case=c['id'],config=cfg,seconds=r['complete_seconds'],success=r['success'],fallback=r['fallback_count'])
    assert r['success'],(c['id'],cfg)
def medians(c,split,reps):
 return [statistics.median(st.read(st.HERE/split/f'{c["id"]}_{canonical(c,cfg)}_{r}.json.gz')['complete_seconds'] for r in range(reps)) for cfg in BASE]
def features(c):
 ts=c['targets'];n=c['definition']['physical_propagators']
 dots=[sum(max(0,a-1) for a in t) for t in ts];rank=[sum(max(0,-a) for a in t) for t in ts]
 lines=[sum(a>0 for a in t) for t in ts]
 return [len(ts),max(dots),max(rank),min(lines),max(lines),statistics.mean(dots),statistics.mean(rank),len(st.sectors(c)),n]
def structure(c):
 d=c['definition']
 return dict(loops=d['loop_momenta'],external=d['external_momenta'],physical=d['physical_propagators'],
  propagators=[[p['momentum'],p['mass_squared']=='0'] for p in d['propagators']],invariants=d['invariants'])
def fit(cases):
 import numpy as np
 all_models={};begin=time.perf_counter()
 for kind in st.KINDS:
  cs=[c for c in cases if c['split']=='training' and c['topology_group']==kind]
  x=np.array([features(c) for c in cs],dtype=float);times=np.array([medians(c,'training',2) for c in cs]);y=np.log(times/times[:,0,None])
  models=[dict(name='constant',type='constant',value=y.mean(axis=0).tolist())]
  def tree(ids,depth):
   nodes=[]
   def build(ids,level):
    idx=len(nodes);value=y[ids].mean(axis=0);nodes.append(dict(feature=-1,value=value.tolist(),rows=len(ids)))
    if level==depth or len(ids)<2:return idx
    loss=float(((y[ids]-value)**2).sum());best=None
    for f in range(x.shape[1]):
     v=np.unique(x[ids,f])
     for cut in (v[:-1]+v[1:])/2:
      a=ids[x[ids,f]<=cut];b=ids[x[ids,f]>cut]
      if not len(a) or not len(b):continue
      new=float(((y[a]-y[a].mean(axis=0))**2).sum()+((y[b]-y[b].mean(axis=0))**2).sum())
      if new<loss-1e-12:loss=new;best=(f,float(cut),a,b)
    if best:
     f,cut,a,b=best;left=build(a,level+1);right=build(b,level+1);nodes[idx].update(feature=f,threshold=cut,left=left,right=right)
    return idx
   build(ids,0);return dict(type='tree',nodes=nodes)
  for depth in [1,2,3]:models.append(dict(tree(np.arange(len(x)),depth),name=f'tree{depth}'))
  rng=np.random.RandomState(14026)
  forest=[tree(rng.randint(len(x),size=len(x)),3) for _ in range(16)]
  models.append(dict(name='forest16',type='forest',trees=forest))
  mu=x.mean(axis=0);sd=x.std(axis=0);sd[sd<1e-10]=1;z=np.c_[np.ones(len(x)),(x-mu)/sd]
  for alpha in [.1,1.,10.]:
   penalty=np.eye(z.shape[1])*alpha;penalty[0,0]=0
   beta=np.linalg.solve(z.T@z+penalty,z.T@y)
   models.append(dict(name=f'ridge{alpha}',type='ridge',mean=mu.tolist(),scale=sd.tolist(),coefficients=beta.tolist()))
  for k in [1,3]:models.append(dict(name=f'nearest{k}',type='nearest',k=k,x=x.tolist(),y=y.tolist(),scale=sd.tolist()))
  all_models[kind]=dict(models=models,training_cases=[c['id'] for c in cs],training_features=x.tolist(),training_log_costs=y.tolist(),fixed=BASE[int(np.argmin(y.mean(axis=0)))])
 r=dict(families=all_models,configurations=BASE,training_seconds=time.perf_counter()-begin,
  feature_names=['targets','maximum_dots','maximum_rank','minimum_lines','maximum_lines','mean_dots','mean_rank','maximal_target_sectors','physical_propagators'])
 st.write(st.HERE/'trained_model/candidates.json',r);st.emit(stage='fit',families=len(all_models),models=sum(len(v['models']) for v in all_models.values()),seconds=r['training_seconds'])
 return r
def predict(m,x):
 if m['type']=='constant':return m['value']
 if m['type']=='tree':
  i=0
  while m['nodes'][i]['feature']>=0:
   n=m['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
  return m['nodes'][i]['value']
 if m['type']=='forest':
  ys=[predict(t,x) for t in m['trees']]
  return [statistics.mean(y[j] for y in ys) for j in range(len(BASE))]
 if m['type']=='nearest':
  ids=sorted(range(len(m['x'])),key=lambda i:sum(((a-b)/s)**2 for a,b,s in zip(x,m['x'][i],m['scale'])))[:m['k']]
  return [statistics.mean(m['y'][i][j] for i in ids) for j in range(len(BASE))]
 z=[1]+[(a-b)/s for a,b,s in zip(x,m['mean'],m['scale'])]
 return [sum(z[i]*m['coefficients'][i][j] for i in range(len(z))) for j in range(len(BASE))]
def choose(m,c,gate=0.):
 scores=predict(m,features(c));j=min(range(len(BASE)),key=scores.__getitem__)
 return canonical(c,BASE[j] if scores[j]<scores[0]-gate else 'native')
def geo(values):return math.exp(statistics.mean(map(math.log,values)))
def freeze(cases,trained):
 policies={}
 for kind,fam in trained['families'].items():
  cs=[c for c in cases if c['split']=='validation' and c['topology_group']==kind];cost=[medians(c,'validation',3) for c in cs]
  fixed=fam['fixed'];controls=['native','sector_truncate0',fixed]
  control=min(controls,key=lambda cfg:geo([t[BASE.index(cfg)]/t[0] for t in cost]))
  options=[]
  for m in fam['models']:
   for gate in [0.,.05,.15]:
    decisions=[choose(m,c,gate) for c in cs]
    ratios=[t[BASE.index(cfg)]/t[BASE.index(control)] for cfg,t in zip(decisions,cost)]
    options.append(dict(model=m['name'],gate=gate,ratio_to_control=geo(ratios),decisions=decisions))
  best=min(options,key=lambda r:r['ratio_to_control']);enabled=best['ratio_to_control']<=.95
  policies[kind]=dict(model=next(m for m in fam['models'] if m['name']==best['model']),gate=best['gate'],enabled=enabled,
   validation_control=control,best_fixed=fixed,validation=best,options=options,
   structure=structure(cs[0]),
   features_min=[min(x[j] for x in fam['training_features']) for j in range(9)],features_max=[max(x[j] for x in fam['training_features']) for j in range(9)])
 manifest={p.name:sha(p) for p in [st.HERE/n for n in ['s00_study.py','s02_native.py','s03_truncate.py','s04_train_test.py','protocol.json']]}
 r=dict(policies=policies,manifest=manifest,previous_freeze_sha256=sha(st.previous.HERE/'trained_model/freeze.json'),binary_sha256=sha(st.previous.BINARY),repetitions=5,tests_not_used=True)
 p=st.HERE/'trained_model/freeze.json'
 assert not list((st.HERE/'model_test').glob('*.json.gz')),'Do not refit after tests'
 st.write(p,r);st.emit(stage='frozen',policies={k:dict(model=v['model']['name'],enabled=v['enabled'],control=v['validation_control'],validation_ratio=v['validation']['ratio_to_control']) for k,v in policies.items()})
 return r
def select(f,c):
 p=f['policies'].get(c['topology_group'])
 if p is None:return 'native','unknown_graph'
 if structure(c)!=p['structure']:return 'native','different_structure'
 x=features(c)
 if any(v<lo or v>hi for v,lo,hi in zip(x,p['features_min'],p['features_max'])):return 'native','feature_range'
 if not p['enabled']:return canonical(c,p['validation_control']),'validation_control'
 return choose(p['model'],c,p['gate']),'learned'
def check_freeze(f):
 for name,h in f['manifest'].items():assert sha(st.HERE/name)==h,name
 assert sha(st.previous.BINARY)==f['binary_sha256']
 assert sha(st.previous.HERE/'trained_model/freeze.json')==f['previous_freeze_sha256']
 old=json.loads((st.previous.HERE/'trained_model/freeze.json').read_text())
 for p,h in old['weights'].items():assert sha(st.ROOT/p)==h,p
 for p,key in [(st.previous.HERE/'s05_study.py','source_sha256'),(st.previous.HERE/'s02_run.py','driver_sha256')]:assert sha(p)==old[key]
def test(cases,f):
 check_freeze(f)
 methods=['native','deterministic','family_fixed','learned']
 for case_number,c in enumerate(c for c in cases if c['split']=='reserved'):
  ref=st.reference(c)
  for rep in range(5):
   offset=(case_number+rep)%4
   order=methods[offset:]+methods[:offset]
   for method in order:
    p=st.HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
    if p.exists():continue
    begin=time.perf_counter()
    if method=='learned':cfg,reason=select(f,c)
    else:cfg=canonical(c,'native' if method=='native' else 'sector_truncate0' if method=='deterministic' else f['policies'][c['topology_group']]['best_fixed']);reason=method
    inference=time.perf_counter()-begin;r=st.workflow(c,ref,cfg);r.update(complete_seconds=time.perf_counter()-begin,method=method,repetition=rep,decision_seconds=inference,selection_reason=reason)
    st.save(p,r);st.emit(stage='test',case=c['id'],method=method,config=cfg,reason=reason,seconds=r['complete_seconds'],success=r['success'],fallback=r['fallback_count'])
    assert r['success'],(c['id'],method)
  p=st.HERE/'model_test'/f'{c["id"]}_application.json.gz'
  if not p.exists():
   want=st.read(ref);cfg,reason=select(f,c);r=st.workflow(c,None,cfg,basis=want['masters']);assert r['success']
   got=r['attempts'][-1]['coefficients'];assert set(got)==set(want['coefficients']);checks=0
   import sympy as sp
   for target,row in got.items():
    expected=want['coefficients'][target]
    for m in set(row)|set(expected):
     a,b=row.get(m,'0'),expected.get(m,'0')
     assert a==b or sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))==0
     checks+=1
   r.update(reference_coefficients_withheld=True,independent_exact_checks=checks,all_exact=True,selection_reason=reason);st.save(p,r)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['develop','test','all']);a=ap.parse_args();cases=prepare()
 if a.stage in ['develop','all']:
  assert not (st.HERE/'trained_model/freeze.json').exists()
  measure(cases,'training',2);measure(cases,'validation',3);freeze(cases,fit(cases))
 if a.stage in ['test','all']:test(cases,json.loads((st.HERE/'trained_model/freeze.json').read_text()))
if __name__=='__main__':main()
