"""Compare family-specific choices using complete exact reduction cost."""
import copy,gzip,hashlib,json,math,os,statistics,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_workflow_selection'))
import s05_study as previous
from s02_run import run
KINDS=previous.KINDS
CAP=12*1024**2

def emit(**r): print(json.dumps(r),flush=True)
def read(p): return json.load(gzip.open(p,'rt'))
def write(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(r,indent=2)+'\n')
def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
 assert len(data)<1024**2
 used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())
 assert used+len(data)+4096<CAP,(used,len(data))
 tmp=p.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(p)
def compact(r):
 r=copy.deepcopy(r)
 if 'log' in r:
  r['log_sha256']=hashlib.sha256(r['log'].encode()).hexdigest()
  if not r['success']:r['failure_log_tail']=r['log'][-5000:]
  del r['log']
 totals={}
 for x in r.get('stage_metrics',[]):totals[x['stage']]=totals.get(x['stage'],0.)+x['seconds']
 r['stage_totals']=totals;r.pop('stage_metrics',None)
 for k in ['raw_export','metrics']:r.pop(k,None)
 return r
def definition(kind,h):
 templates=json.loads((ROOT/'ML_model_workflow_selection/cases.json').read_text())['cases']
 if kind in previous.study.KINDS:return previous.study.build(kind,False,h)
 d=copy.deepcopy(next(c['definition'] for c in templates if c['topology_group']==kind))
 a,b=1009+12*h,1021+14*h
 if kind in ['sunrise','ladder3']:
  d['scalarproduct_rules']=[[['p','p'],str(-a)]];d['parameters']['p2']=-a
 elif kind=='double_box':
  d['scalarproduct_rules']=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'-{a}/2'],[['p1','p3'],f'-{b}/2'],[['p2','p3'],f'{a+b}/2']]
  d['parameters'].update(s=-a,t=-b)
 else:
  d['propagators'][-1]['mass_squared']=str(53+2*h);d['parameters']['masses'][-1]=53+2*h
 return d
def make_case(kind,h,shape,split='training'):
 d=definition(kind,h);n=len(d['propagators']);t=d['physical_propagators']
 corner=[int(i<t) for i in range(n)];ts=[]
 if shape=='top':
  for j in range(min(t,3)):
   a=corner.copy();a[j]+=2;ts.append(a)
 elif shape=='pinch':
  # A single lower sector and its first three dotted targets.
  corner[0]=0
  if t>=5:corner[2]=0
  ts.append(corner.copy())
  for j in [i for i in range(t) if corner[i]][:3]:
   a=corner.copy();a[j]+=1;ts.append(a)
 elif shape=='numerator':
  for j in range(t,min(n,t+3)):
   a=corner.copy();a[j]=-2;ts.append(a)
  if not ts:
   for j in range(min(t,3)):
    a=corner.copy();a[j]=3;ts.append(a)
 else:raise ValueError(shape)
 cid=f'{kind}_p{h}_{shape}'
 return dict(id=cid,group=f'{kind}_p{h}',split=split,topology_group=kind,shape=shape,definition=d,targets=ts,size=len(ts))
def sectors(c):
 masks={sum(1<<i for i,a in enumerate(t) if a>0) for t in c['targets']}
 return sorted(m for m in masks if not any(m!=n and m&n==m for n in masks))
def seed_bounds(c,config,margin=0):
 ts=c['targets'];base=[max(sum(max(0,a) for a in t) for t in ts),max(sum(max(0,-a) for a in t) for t in ts),max(sum(max(0,a-1) for a in t) for t in ts)]
 if config=='expanded':margin=1
 raw=[v+margin for v in base]
 if config.endswith('tight'):raw=[max(0,a+b) for a,b in zip(base,[-1,0,-1])]
 bounds=raw.copy()
 bounds[0]=max(bounds[0],max(bin(v).count('1') for v in c['definition']['top_level_sectors']))
 return raw,bounds
def attempt(c,ref,config,margin=0,basis=None):
 cc=copy.deepcopy(c)
 if config.startswith('sector'):cc['definition']['top_level_sectors']=sectors(c)
 task='equation' if config.endswith('equation') else 'seed' if config=='seed' else 'native'
 w=previous.weights(c,task)
 threshold=.01
 if w and c['topology_group'] in previous.study.KINDS:
  f=json.loads((previous.study.HERE/'freeze.json').read_text())
  threshold=f['policies'][c['topology_group']+'_'+task]['threshold']
 previous.study.setup('learned' if w else 'off',w,threshold)
 os.environ.update(KIRA_RUNTIME_BINARY=str(previous.BINARY),KIRA_EPHEMERAL_DB='1')
 if config=='expanded':margin=1
 requested,bounds=seed_bounds(cc,config,margin)
 r=run(cc,c['size'],'native',HERE/'unused',timeout=120,margin=margin,reference=ref,records=False,archive=False,
  check_masters=bool(ref or basis),scratch_cap=32*1024**2,ordering=5 if config=='order5' else 1,basis=basis,bounds=bounds)
 r['configuration']=config
 r['requested_seed_bounds']=requested
 r['positive_bound_floor_applied']=bounds[0]!=requested[0]
 return r
def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if not p.exists():
  r=attempt(c,None,'native',margin=1);save(p,compact(r));emit(stage='reference',case=c['id'],success=r['success'],status=r['status'],seconds=r['complete_seconds'])
 assert read(p)['success'],c['id']
 return p
def workflow(c,ref,config,basis=None):
 begin=time.perf_counter();attempts=[]
 plan=[(config,0)]+([('native',0)] if config!='native' else [])+[('native',1)]
 for cfg,margin in plan:
  r=attempt(c,ref,cfg,margin,basis);attempts.append(compact(r))
  if r['success'] or r.get('mismatches'):break
 return dict(case=c['id'],configuration=config,success=attempts[-1]['success'],fallback_count=len(attempts)-1,complete_seconds=time.perf_counter()-begin,attempts=attempts)
def pilot():
 cases=[make_case(k,61,s) for k in KINDS for s in ['top','pinch','numerator']]
 write(HERE/'pilot_cases.json',dict(cases=cases))
 for c in cases:
  ref=reference(c)
  configs=['native','sector','tight','equation','expanded']
  for cfg in configs:
   if cfg=='sector' and sectors(c)==c['definition']['top_level_sectors']:continue
   p=HERE/'development'/f'{c["id"]}_{cfg}.json.gz'
   if p.exists():continue
   r=workflow(c,ref,cfg);save(p,r)
   emit(stage='pilot',case=c['id'],config=cfg,success=r['success'],fallback=r['fallback_count'],seconds=r['complete_seconds'])
   assert r['success']
if __name__=='__main__':pilot()
