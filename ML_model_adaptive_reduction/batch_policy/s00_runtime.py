"""Partition physical targets before native Kira equation generation."""
import copy,gzip,json,math,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FILTER=ROOT/'ML_model_equation_selection/bound_refinement'
sys.path.insert(0,str(FILTER))
from s00_probe import rt,inputs
ACTIONS=['whole','rank','dots','sector','chunks3','whole_off']

def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 raw=gzip.compress(json.dumps(d,separators=(',',':')).encode(),mtime=0)
 used=sum(q.stat().st_blocks*512 for q in HERE.rglob('*') if q.is_file())
 assert used+len(raw)+4096<32*1024**2,'Study storage limit'
 p.write_bytes(raw)

def partition(c,action):
 if action=='whole_off':action='whole'
 groups={}
 for i,a in enumerate(c['targets']):
  key={'whole':0,'rank':sum(max(0,-v) for v in a),'dots':sum(max(0,v-1) for v in a),'sector':tuple(v>0 for v in a),'chunks3':i//3}[action]
  groups.setdefault(key,[]).append(a)
 out=[]
 for i,ts in enumerate(groups.values()):
  q=copy.deepcopy(c);q.update(id=c['id']+'_part'+str(i),targets=ts,size=len(ts));out.append(q)
 assert sorted(tuple(a) for q in out for a in q['targets'])==sorted(tuple(a) for a in c['targets'])
 return out

def feature(c):
 x=inputs.features(c);ts=c['targets'];dots=[sum(max(0,v-1) for v in a) for a in ts];ranks=[sum(max(0,-v) for v in a) for a in ts]
 x.extend([len(set(dots)),len(set(ranks)),max(dots)-min(dots),max(ranks)-min(ranks),sum(d*r for d,r in zip(dots,ranks))/len(ts)])
 return x

def settings(c,ml):
 # The ML-off path loads only fixed settings and physical signatures.
 cfg=rt.read(HERE/'fixed_inputs.json');matches=[g for g,s in cfg['signatures'].items() if inputs.signature(c) in s]
 g=matches[0] if len(matches)==1 else None
 action=cfg['seed_actions'].get(g,'native');option=None
 if ml and g:
  f=rt.read(FILTER/'trained_model/freeze.json');d=f['features'][g];x=inputs.features(c)
  if all(d['minimum'][i]-1e-9<=x[i]<=d['maximum'][i]+1e-9 for i in [5,6,7,21,25]):option=f['selection'].get(g,{}).get('option')
 return action,option

def attempt(c,basis,action,option=None,timeout=60,custom=None):
 with rt.environment():
  if option:
   weight=FILTER/'trained_model'/(option['name']+'.txt')
   cfg=rt.read(HERE/'fixed_inputs.json');assert inputs.sha(weight)==cfg['filter_hashes'][option['name']]
   os.environ.update(KIRA_EQ_MODE='learned',KIRA_EQ_WEIGHTS=str(weight),KIRA_EQ_THRESHOLD=str(option['threshold']))
  return rt.native.run(c,c['size'],'native',HERE/'unused',timeout=timeout,margin=0,archive=False,records=False,basis=basis,check_masters=basis is not None,scratch_cap=32*1024**2,bounds=custom or inputs.bounds(c,action),ordering=1,threads=1,truncate=inputs.truncation(c,action))

def run(c,basis,action='whole',ml=True,reference=None,limit=150):
 if action=='whole_off':ml=False
 start=time.perf_counter();validate(c,basis);groups=partition(c,action);out={};attempts=[];ok=True;fallbacks=0
 for sub in groups:
  seed,opt=settings(sub,ml);seq=[(seed,opt)]
  if opt:seq.append((seed,None))
  seq.extend((a,None) for a in ['native','expanded'] if a!=seed)
  seen=set();success=False
  for seed,opt in seq:
   key=(tuple(inputs.bounds(sub,seed)),inputs.truncation(sub,seed),json.dumps(opt,sort_keys=True))
   if key in seen:continue
   seen.add(key);left=limit-(time.perf_counter()-start)
   if left<12:break
   r=attempt(sub,basis,seed,opt,timeout=min(60,left));r.update(batch_action=action,seed_action=seed,filter_option=opt)
   compact=rt.compact(r);compact.pop('coefficients',None);attempts.append(compact)
   if r['success']:
    out.update(r['coefficients']);success=True;break
   fallbacks+=1
  if not success:ok=False;break
 if not ok and action not in ['whole','whole_off'] and limit-(time.perf_counter()-start)>=12:
  recovery=run(c,basis,'whole',False,None,limit-(time.perf_counter()-start))
  attempts.extend(recovery['attempts']);fallbacks+=1+recovery['fallbacks'];out=recovery['coefficients'];ok=recovery['success']
 r=dict(case=c['id'],action=action,filter_enabled=ml,groups=len(groups),success=ok,coefficients=out,attempts=attempts,fallbacks=fallbacks,reference_coefficients_supplied=False,basis_supplied=True)
 if reference:rt.verify(r,reference)
 r['complete_seconds']=time.perf_counter()-start;return r

def predict(model,x):
 import struct
 x=[struct.unpack('f',struct.pack('f',v))[0] for v in x];scores=[0.]*len(ACTIONS)
 for t in model['trees']:
  i=0
  while t['left'][i]>=0:i=t['left'][i] if x[t['feature'][i]]<=t['cut'][i] else t['right'][i]
  for j,v in enumerate(t['value'][i]):scores[j]+=v/len(model['trees'])
 return scores

def equivalent_partitions(c):
 if len(c['targets'])>3:return False
 keys={(sum(max(0,-v) for v in a),sum(max(0,v-1) for v in a),tuple(v>0 for v in a)) for a in c['targets']}
 return len(keys)==1 and settings(c,True)[1] is None

def choose(c,freeze):
 if equivalent_partitions(c):return 'whole_off',None
 x=feature(c);sig=inputs.signature(c);matches=[g for g,d in freeze['domain'].items() if sig in d['signatures']]
 if len(matches)!=1:return 'whole',None
 g=matches[0];d=freeze['domain'][g]
 if any(x[i]<d['minimum'][i]-1e-9 or x[i]>d['maximum'][i]+1e-9 for i in [5,6,7,21,25]):return 'whole',None
 fixed=freeze['fixed_by_graph'].get(g,'whole')
 if not freeze.get('enabled',True):return fixed,None
 scores=predict(freeze['model'],x);a=min(range(len(ACTIONS)),key=scores.__getitem__)
 return (ACTIONS[a] if scores[a]<scores[ACTIONS.index(fixed)]-freeze['gate'] else fixed),scores

def reduce(c,basis,method='learned',reference=None):
 start=time.perf_counter();validate(c,basis);scores=None
 if method=='learned' and equivalent_partitions(c):action='whole_off';ml=False
 elif method=='learned':f=rt.read(HERE/'trained_model/freeze.json');action,scores=choose(c,f);ml=True
 elif method=='fixed':action=rt.read(HERE/'trained_model/fixed.json')['by_graph'].get(c['topology_group'],'whole');ml=True
 elif method=='fixed_off':action=rt.read(HERE/'trained_model/fixed.json')['off_by_graph'].get(c['topology_group'],'whole');ml=False
 elif method=='previous':action='whole';ml=True
 elif method=='off':action='whole';ml=False
 else:raise ValueError(method)
 selection=time.perf_counter()-start;r=run(c,basis,action,ml,reference);r.update(method=method,decision_seconds=selection,scores=scores,prediction_skipped_equivalent_partitions=method=='learned' and equivalent_partitions(c),complete_seconds=time.perf_counter()-start);return r

def validate(c,basis):
 n=len(c['definition']['propagators']);tops=c['definition']['top_level_sectors']
 if not 0<n<=31 or c['size']!=len(c['targets']) or not c['targets']:raise ValueError('Unsupported integral-index count or target list')
 if c['definition'].get('cut_propagators') or c['definition'].get('symbolic_ibp'):raise ValueError('Unsupported family definition')
 if not tops or any(type(s) is not int or not 0<s<2**n for s in tops):raise ValueError('Invalid sector')
 if len(set(map(tuple,c['targets'])))!=len(c['targets']):raise ValueError('Duplicate target')
 for a in c['targets']+basis:
  if len(a)!=n or any(type(v) is not int for v in a):raise ValueError('Invalid integral index vector')
  s=sum(1<<i for i,v in enumerate(a) if v>0)
  if not any(s&t==s for t in tops):raise ValueError('Target or master lies outside declared sectors')

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--basis',required=True);p.add_argument('--output',required=True);p.add_argument('--method',default='learned',choices=['learned','fixed','fixed_off','previous','off']);a=p.parse_args()
 r=reduce(rt.read(a.case),rt.read(a.basis),a.method);save(a.output,r);print(json.dumps(dict(success=r['success'],seconds=r['complete_seconds'],partition=r['action'])))
