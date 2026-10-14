"""Train complete-cost selectors and test frozen policies on fresh reductions."""
import argparse,copy,gzip,hashlib,json,math,os,statistics,sys,time
from pathlib import Path
from s00_pilot import HERE,ROOT,study,save
sys.path.insert(0,str(HERE))
from s02_run import run

KINDS=['sunrise','double_box','vacuum3','ladder3','nonplanar_box','pentagon','one_mass_box']
CONFIGS=['fixed','tight','dots','equation','seed','order5','expanded']
BINARY=ROOT/'.tools/kira-workflow/kira'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.load(gzip.open(p,'rt'))
def write(p,r):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2)+'\n')
def emit(**r):print(json.dumps(r),flush=True)

def prepare():
 old=json.loads((ROOT/'ML_model_equation_selection/early_generation/families_test.json').read_text())['cases']
 templates={c['topology_group']:c for c in old};cases=[]
 for split,profiles in [('training',[41,42]),('validation',[43]),('reserved',[44,45])]:
  for kind in KINDS:
   for profile in profiles:
    if kind in study.KINDS:
     d=study.build(kind,False,profile);ts=study.targets(d)
    else:
     d=copy.deepcopy(templates[kind]['definition']);ts=templates[kind]['targets']
     # New exact rational kinematics. Preserve each graph and its mass pattern.
     a,b=1009+12*profile,1021+14*profile
     if kind in ['sunrise','ladder3']:
      d['scalarproduct_rules']=[[['p','p'],str(-a)]];d['parameters']['p2']=-a
     elif kind=='double_box':
      d['scalarproduct_rules']=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'-{a}/2'],[['p1','p3'],f'-{b}/2'],[['p2','p3'],f'{a+b}/2']]
      d['parameters'].update(s=-a,t=-b)
     else:
      d['propagators'][-1]['mass_squared']=str(53+2*profile);d['parameters']['masses'][-1]=53+2*profile
    sizes=[4,min(32,len(ts))]
    for size in sizes:
     cid=f'{kind}_p{profile}_n{size}'
     cases.append(dict(id=cid,group=f'{kind}_p{profile}',split=split,topology_group=kind,definition=d,targets=ts[:size],size=size))
  for kind in study.KINDS:
   # The new symbolic target lists are disjoint from the prior symbolic split.
   start={'training':12,'validation':16,'reserved':20}[split]
   d=study.build(kind,True);ts=study.targets(d)
   # The one-mass box has 21 targets. Use new double-dot targets instead.
   corner=[int(i<d['physical_propagators']) for i in range(len(d['propagators']))]
   extras=[]
   for i in range(d['physical_propagators']):
    t=corner.copy();t[i]+=2;extras.append(t)
   if kind=='one_mass_box':
    offset={'training':0,'validation':1,'reserved':2}[split];selected=[extras[offset]]
   else:selected=ts[start:start+4]
   assert selected
   cid=f'{kind}_symbolic_{split}'
   cases.append(dict(id=cid,group=cid,split=split,topology_group=kind,definition=d,targets=selected,size=len(selected)))
 for kind in KINDS:
  groups={s:{c['group'] for c in cases if c['topology_group']==kind and c['split']==s} for s in ['training','validation','reserved']}
  assert not groups['training']&groups['reserved'] and not groups['validation']&groups['reserved']
 record=dict(cases=cases,configurations=CONFIGS,training_repetitions=3,validation_repetitions=3,test_repetitions=5,
  scope='Known graph structures at new rational points and new symbolic target lists; native IBP generation at one to three loops.',
  tests_frozen_before_execution=True)
 p=HERE/'cases.json'
 if p.exists():assert json.loads(p.read_text())==record
 else:write(p,record)
 for name in ['references','training','validation','trained_model','model_test']: (HERE/name).mkdir(exist_ok=True)
 emit(stage='prepared',cases=len(cases))

def features(c):
 d=c['definition'];ts=c['targets'];dots=[sum(max(0,a-1) for a in t) for t in ts];rank=[sum(max(0,-a) for a in t) for t in ts]
 return [len(d['loop_momenta']),len(d['external_momenta']),len(d['propagators']),d['physical_propagators'],len(d['invariants']),math.log1p(len(ts)),max(dots),max(rank),statistics.mean(dots),statistics.mean(rank),len({tuple(a>0 for a in t) for t in ts})]+[int(c['topology_group']==k) for k in KINDS]

def weights(c,task):
 if task not in ['seed','equation']:return None
 if c['topology_group'] in study.KINDS:
  return study.model_path(c,task)
 if task=='equation':return study.OLD
 return None

def attempt(c,ref,config,margin=0,basis=None):
 task=config if config in ['seed','equation'] else 'native';w=weights(c,task)
 threshold=.01
 if c['topology_group'] in study.KINDS and task!='native':
  f=json.loads((study.HERE/'freeze.json').read_text());threshold=f['policies'][c['topology_group']+'_'+task]['threshold']
 study.setup('learned' if w else 'off',w,threshold)
 os.environ['KIRA_RUNTIME_BINARY']=str(study.BINARY if config=='native' else BINARY)
 os.environ['KIRA_EPHEMERAL_DB']='0' if config=='native' else '1'
 if config=='expanded':margin=1
 bounds=None
 if config in ['tight','dots']:
  ts=c['targets'];base=[max(sum(max(0,a) for a in t) for t in ts),max(sum(max(0,-a) for a in t) for t in ts),max(sum(max(0,a-1) for a in t) for t in ts)]
  delta=(-1,-1,-1) if config=='tight' else (-1,0,-1)
  bounds=[max(0,a+b) for a,b in zip(base,delta)]
 return run(c,c['size'],'native',HERE/'unused',timeout=120,margin=margin,reference=ref,records=False,archive=False,
   check_masters=bool(ref or basis),scratch_cap=32*1024**2,ordering=5 if config=='order5' else 1,basis=basis,bounds=bounds)

def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if not p.exists():
  r=attempt(c,None,'native',margin=1);save(p,r);emit(stage='reference',case=c['id'],success=r['success'],seconds=r['complete_seconds'])
 assert read(p)['success'],c['id']
 return p

def workflow(c,ref,config,basis=None):
 start=time.perf_counter();attempts=[]
 plan=[(config,0)]+([('fixed',0)] if config not in ['fixed','native'] else [])+[(('native' if config=='native' else 'fixed'),1)]
 for cfg,margin in plan:
  r=attempt(c,ref,cfg,margin,basis);attempts.append(r)
  if r['success'] or r.get('mismatches'):break
 return dict(case=c['id'],configuration=config,success=attempts[-1]['success'],fallback_count=len(attempts)-1,
  complete_seconds=time.perf_counter()-start,attempts=attempts)

def measurements(cases,split,reps):
 for c in cases:
  if c['split']!=split:continue
  ref=reference(c)
  for rep in range(reps):
   order=CONFIGS[rep%len(CONFIGS):]+CONFIGS[:rep%len(CONFIGS)]
   for cfg in order:
    p=HERE/split/f'{c["id"]}_{cfg}_{rep}.json.gz'
    if p.exists():continue
    r=workflow(c,ref,cfg);r['repetition']=rep;save(p,r)
    emit(stage=split,case=c['id'],config=cfg,success=r['success'],fallback=r['fallback_count'],seconds=r['complete_seconds'])
    assert r['success'],(c['id'],cfg)

def medians(c,split,reps):
 return [statistics.median(read(HERE/split/f'{c["id"]}_{cfg}_{r}.json.gz')['complete_seconds'] for r in range(reps)) for cfg in CONFIGS]

def train(cases):
 import numpy as np
 cs=[c for c in cases if c['split']=='training'];x=np.array([features(c) for c in cs]);times=np.array([medians(c,'training',3) for c in cs]);y=np.log(times/times[:,0,None]);models=[]
 # A constant predictor is the fixed-strategy control.
 models.append(dict(name='constant',type='constant',value=y.mean(axis=0).tolist()))
 def tree(depth):
  nodes=[]
  def make(ids,level):
   i=len(nodes);nodes.append(dict(feature=-1,value=y[ids].mean(axis=0).tolist(),rows=len(ids)))
   if level==depth or len(ids)<6:return i
   best=None;loss=float(((y[ids]-y[ids].mean(axis=0))**2).sum())
   for f in range(x.shape[1]):
    u=np.unique(x[ids,f])
    for cut in (u[:-1]+u[1:])/2:
     mask=x[ids,f]<=cut
     if min(mask.sum(),(~mask).sum())<3:continue
     a,b=ids[mask],ids[~mask];new=float(((y[a]-y[a].mean(axis=0))**2).sum()+((y[b]-y[b].mean(axis=0))**2).sum())
     if new<loss-1e-10:loss=new;best=(f,float(cut),a,b)
   if best:
    f,cut,a,b=best;left=make(a,level+1);right=make(b,level+1);nodes[i].update(feature=f,threshold=cut,left=left,right=right)
   return i
  make(np.arange(len(cs)),0)
  return dict(name=f'tree{depth}',type='tree',nodes=nodes)
 models.extend(tree(d) for d in [2,4,6])
 mu=x.mean(axis=0);scale=x.std(axis=0);scale[scale<1e-10]=1;z=np.c_[np.ones(len(x)),(x-mu)/scale]
 for alpha in [.1,1.,10.]:
  penalty=np.eye(z.shape[1])*alpha;penalty[0,0]=0
  beta=np.linalg.solve(z.T@z+penalty,z.T@y)
  models.append(dict(name=f'ridge{alpha}',type='ridge',mean=mu.tolist(),scale=scale.tolist(),coefficients=beta.tolist(),alpha=alpha))
 for k in [2,4]:models.append(dict(name=f'nearest{k}',type='nearest',k=k,scale=scale.tolist(),x=x.tolist(),y=y.tolist()))
 out=dict(models=models,configurations=CONFIGS,training_cases=[c['id'] for c in cs],feature_names=['loops','external_momenta','indices','physical_propagators','symbolic_invariants','log_one_plus_targets','maximum_dots','maximum_rank','mean_dots','mean_rank','target_sectors']+KINDS,
  objective='Predict log complete-time ratios to the integrated native strategy, including exact fallback costs.',rows=len(cs),source_sha256=sha(__file__))
 write(HERE/'trained_model/candidates.json',out);emit(stage='trained',models=len(models),rows=len(cs))

def predict(model,c):
 x=features(c)
 if model['type']=='constant':return model['value']
 if model['type']=='nearest':
  eligible=[i for i,v in enumerate(model['x']) if v[:5]==x[:5] and v[11:]==x[11:]]
  if not eligible:return [0.]*len(CONFIGS)
  ids=sorted(eligible,key=lambda i:sum(((a-b)/s)**2 for a,b,s in zip(x,model['x'][i],model['scale'])))[:model['k']]
  return [statistics.mean(model['y'][i][j] for i in ids) for j in range(len(CONFIGS))]
 if model['type']=='tree':
  nodes=model['nodes'];i=0
  while nodes[i]['feature']>=0:
   n=nodes[i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
  return nodes[i]['value']
 z=[1]+[(v-m)/s for v,m,s in zip(x,model['mean'],model['scale'])]
 return [sum(z[i]*model['coefficients'][i][j] for i in range(len(z))) for j in range(len(CONFIGS))]

def choose(model,c,gate=0.):
 scores=predict(model,c);j=min(range(len(scores)),key=scores.__getitem__)
 return CONFIGS[j] if scores[j]<scores[0]-gate else 'fixed'

def freeze(cases):
 candidates=json.loads((HERE/'trained_model/candidates.json').read_text());cs=[c for c in cases if c['split']=='validation'];options=[]
 for model in candidates['models']:
  for gate in [0.,.05,.15]:
   ratios=[];decisions=[]
   for c in cs:
    t=medians(c,'validation',3);cfg=choose(model,c,gate);ratios.append(t[CONFIGS.index(cfg)]/t[0]);decisions.append(dict(case=c['id'],config=cfg))
   options.append(dict(model=model['name'],gate=gate,ratio=math.exp(statistics.mean(map(math.log,ratios))),decisions=decisions))
 best=min(options,key=lambda r:r['ratio']);model=next(m for m in candidates['models'] if m['name']==best['model'])
 fixed=min(CONFIGS,key=lambda cfg:statistics.mean(math.log(medians(c,'training',3)[CONFIGS.index(cfg)]/medians(c,'training',3)[0]) for c in cases if c['split']=='training'))
 record=dict(model=model,gate=best['gate'],validation=best,options=options,best_fixed=fixed,configurations=CONFIGS,cases_sha256=sha(HERE/'cases.json'),source_sha256=sha(__file__),driver_sha256=sha(HERE/'s02_run.py'),binary_sha256=sha(BINARY),old_binary_sha256=sha(study.BINARY),repetitions=5,
  weights={str(p.relative_to(ROOT)):sha(p) for p in [study.OLD]+[study.model_path(dict(topology_group=k),t) for k in study.KINDS for t in ['seed','equation']]})
 write(HERE/'trained_model/freeze.json',record);emit(stage='frozen',selection=best['model'],gate=best['gate'],ratio=best['ratio'],best_fixed=fixed)

def test(cases):
 f=json.loads((HERE/'trained_model/freeze.json').read_text())
 for p,key in [(HERE/'cases.json','cases_sha256'),(Path(__file__),'source_sha256'),(HERE/'s02_run.py','driver_sha256'),(BINARY,'binary_sha256'),(study.BINARY,'old_binary_sha256')]:assert sha(p)==f[key]
 for p,h in f['weights'].items():assert sha(ROOT/p)==h
 for c in cases:
  if c['split']!='reserved':continue
  ref=reference(c)
  methods=['native','fixed','best_fixed','learned']
  for rep in range(5):
   order=methods[rep%4:]+methods[:rep%4]
   for method in order:
    p=HERE/'model_test'/f'{c["id"]}_{method}_{rep}.json.gz'
    if p.exists():continue
    begin=time.perf_counter()
    cfg=choose(f['model'],c,f['gate']) if method=='learned' else f['best_fixed'] if method=='best_fixed' else method
    decision=time.perf_counter()-begin;r=workflow(c,ref,cfg);r['complete_seconds']=time.perf_counter()-begin
    r.update(method=method,repetition=rep,decision_seconds=decision);save(p,r)
    emit(stage='test',case=c['id'],method=method,config=cfg,success=r['success'],fallback=r['fallback_count'],seconds=r['complete_seconds'])
    assert r['success']
  p=HERE/'model_test'/f'{c["id"]}_application.json.gz'
  if not p.exists():
   want=read(ref);cfg=choose(f['model'],c,f['gate']);r=workflow(c,None,cfg,basis=want['masters'])
   assert r['success'];got=r['attempts'][-1]['coefficients'];assert got.keys()==want['coefficients'].keys();checks=0
   import sympy as sp
   for target,row in got.items():
    expected=want['coefficients'][target]
    for master in set(row)|set(expected):
     left,right=row.get(master,'0'),expected.get(master,'0')
     assert left==right or sp.cancel(sp.sympify(left.replace('^','**'),rational=True)-sp.sympify(right.replace('^','**'),rational=True))==0
     checks+=1
   r.update(answers_withheld=True,independent_coefficient_checks=checks);save(p,r)
 emit(stage='tests_complete')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','collect','train','validate','test','all']);a=ap.parse_args().action
 if a in ['prepare','all']:prepare()
 cases=json.loads((HERE/'cases.json').read_text())['cases']
 if a in ['collect','all']:measurements(cases,'training',3)
 if a in ['train','all']:train(cases)
 if a in ['validate','all']:measurements(cases,'validation',3);freeze(cases)
 if a in ['test','all']:test(cases)
 emit(stage='complete',action=a)
if __name__=='__main__':main()
