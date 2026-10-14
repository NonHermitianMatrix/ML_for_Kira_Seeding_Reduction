"""Fit complete-cost predictors on fresh profiles and freeze before testing."""
import argparse,hashlib,json,math,statistics,time
from pathlib import Path
import s01_workflow as w
features=w.old.features
structure=w.old.structure
BASE=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def medians(c,split,reps):
 return [statistics.median(w.read(w.HERE/split/f'{c["id"]}_{cfg}_{r}.json.gz')['complete_seconds'] for r in range(reps)) for cfg in BASE]
def canonical(c,cfg):return cfg
def fit(cases):
 import numpy as np
 all_models={};begin=time.perf_counter()
 for kind in w.st.KINDS:
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
 w.write(w.HERE/'trained_model/candidates.json',r);w.emit(stage='fit',families=len(all_models),models=sum(len(v['models']) for v in all_models.values()),seconds=r['training_seconds'])
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
def geo(values):return math.exp(statistics.mean(map(math.log,values)))
def prepare(configurations):
 assert configurations[0]=='previous' and len(set(configurations))==len(configurations)
 cs=[c for split,hs in [('training',[72,73]),('validation',[74]),('reserved',[75,76])] for h in hs for c in w.cases(h,split)]
 protocol=dict(cases=cs,configurations=configurations,training_repetitions=2,validation_repetitions=3,test_repetitions=5,
  test_methods=['native','previous','family_fixed','selected'],minimum_validation_gain=.05,
  scope='Seven known graphs at one through three loops. Target index patterns overlap across splits; rational kinematic profiles are separate. The dimension is symbolic.',
  selection='Use validation to choose between the previous route and a training-selected fixed strategy. Enable a new predictor only if it saves at least five percent against that control.')
 p=w.HERE/'protocol.json'
 if p.exists():assert json.loads(p.read_text())==protocol
 else:w.write(p,protocol)
 for d in ['training','validation','trained_model','model_test']:(w.HERE/d).mkdir(exist_ok=True)
 return protocol
def measure(protocol,split):
 reps=protocol[split+'_repetitions']
 for c in protocol['cases']:
  if c['split']!=split:continue
  ref=w.reference(c);basis=w.read(ref)['masters']
  for rep in range(reps):
   order=BASE[rep%len(BASE):]+BASE[:rep%len(BASE)]
   if rep%2:order.reverse()
   for cfg in order:
    p=w.HERE/split/f'{c["id"]}_{cfg}_{rep}.json.gz'
    if p.exists():continue
    r=w.workflow(c,basis,cfg,ref);r['repetition']=rep;w.save(p,r)
    w.emit(stage=split,case=c['id'],configuration=cfg,seconds=r['complete_seconds'],success=r['success'],fallback=r['fallback_count'])
    assert r['success'],(c['id'],cfg)
def freeze(cases,trained):
 policies={}
 assert not list((w.HERE/'model_test').glob('*.json.gz')),'Reserved tests prohibit refitting'
 for kind,fam in trained['families'].items():
  cs=[c for c in cases if c['split']=='validation' and c['topology_group']==kind];cost=[medians(c,'validation',3) for c in cs]
  fixed=fam['fixed'];control=min(['previous',fixed],key=lambda cfg:geo([t[BASE.index(cfg)]/t[0] for t in cost]))
  options=[]
  for m in fam['models']:
   for gate in [0.,.05,.15]:
    choices=[]
    for c in cs:
     scores=predict(m,features(c));j=min(range(len(BASE)),key=scores.__getitem__)
     choices.append(BASE[j] if scores[j]<scores[BASE.index(control)]-gate else control)
    ratio=geo([t[BASE.index(cfg)]/t[BASE.index(control)] for cfg,t in zip(choices,cost)])
    options.append(dict(model=m['name'],gate=gate,ratio_to_control=ratio,decisions=choices))
  best=min(options,key=lambda r:r['ratio_to_control'])
  policies[kind]=dict(model=next(m for m in fam['models'] if m['name']==best['model']),gate=best['gate'],enabled=best['ratio_to_control']<=.95,
   validation_control=control,best_fixed=fixed,validation=best,options=options,structure=structure(cs[0]),
   features_min=[min(x[j] for x in fam['training_features']) for j in range(9)],features_max=[max(x[j] for x in fam['training_features']) for j in range(9)])
 sources=['s00_native.py','s01_workflow.py','s04_train.py','s05_test.py','s07_reduce.py','protocol.json','candidate_selection.json']
 result=dict(policies=policies,configurations=BASE,manifest={p:sha(w.HERE/p) for p in sources},
  previous_freeze_sha256=sha(w.st.HERE/'trained_model/freeze.json'),binary_sha256=sha(w.st.previous.BINARY),tests_not_used=True)
 w.write(w.HERE/'trained_model/freeze.json',result)
 w.emit(stage='frozen',policies={k:dict(enabled=v['enabled'],model=v['model']['name'],control=v['validation_control'],validation=v['validation']['ratio_to_control']) for k,v in policies.items()})
 return result
def check_freeze(f):
 for name,digest in f['manifest'].items():assert sha(w.HERE/name)==digest,name
 assert sha(w.st.HERE/'trained_model/freeze.json')==f['previous_freeze_sha256']
 assert sha(w.st.previous.BINARY)==f['binary_sha256']
 w.old.check_freeze(w.FROZEN)
def select(f,c):
 global BASE
 BASE=f['configurations'];p=f['policies'].get(c['topology_group'])
 if p is None or structure(c)!=p['structure']:return 'previous','unknown_structure'
 x=features(c)
 if any(v<lo or v>hi for v,lo,hi in zip(x,p['features_min'],p['features_max'])):return 'previous','feature_range'
 control=p['validation_control']
 if not p['enabled']:return control,'validation_control'
 scores=predict(p['model'],x);j=min(range(len(BASE)),key=scores.__getitem__)
 return (BASE[j] if scores[j]<scores[BASE.index(control)]-p['gate'] else control),'learned'
def main():
 global BASE
 ap=argparse.ArgumentParser();ap.add_argument('--configurations',nargs='+',required=True);a=ap.parse_args()
 protocol=prepare(a.configurations);BASE=protocol['configurations']
 assert not (w.HERE/'trained_model/freeze.json').exists(),'Keep the published fit unchanged'
 measure(protocol,'training');measure(protocol,'validation');trained=fit(protocol['cases']);freeze(protocol['cases'],trained)
if __name__=='__main__':main()
