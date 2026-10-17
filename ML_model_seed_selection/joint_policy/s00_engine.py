"""Joint seed-boundary and integral-ordering experiments with exact recovery."""
import gzip,hashlib,json,os,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'ML_model_seed_selection/cost_geometry'
sys.path.insert(0,str(OLD))
import s00_policy as geometry
import s03_train as teacher
import s05_reduce as previous
rt=geometry.rt;inputs=geometry.inputs

def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(data,separators=(',',':')).encode()
 if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<2*1024**2
 used=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
 assert used+len(raw)+4096<20*1024**2,'Study storage ceiling'
 path.write_bytes(raw)

def config(graph,name):
 if name=='native':return None,1,None
 parts=name.split('_');kind=parts[0];order=int(parts[1][1:]);permutation=int(parts[2][1:]) if len(parts)>2 else None
 fixed=[1,0,0,-1,0,1,0] if graph=='double_box' else [1,0,0,0,1,1,0]
 choices={'fixed':fixed,'thin':[0,0,0,0,0,1,0],'narrow':[.5,0,0,0,0,1,0],
          'rank':[1,0,0,-2,0,1,0],'wide':[2,0,0,0,0,1,0],
          'full':None,'slope':[1,0,0,1,0,1,-.25]}
 return choices[kind],order,permutation

def make(graph,h,rank,shape,split):
 # Existing constructor supports ranks through four; build higher powers explicitly.
 c=teacher.make(graph,h,min(rank,4),shape,split)
 p=c['definition']['physical_propagators'];a=c['targets'][0];a[p:]=[0]*(len(a)-p)
 i=h%(len(a)-p)
 if shape=='single':a[p+i]=-rank
 else:a[p+(i+1)%(len(a)-p)]=-((rank+1)//2);a[p+i]=-(rank//2)
 c['id']=graph+'_h'+str(h)+'_'+shape+str(rank);c['shape']=shape+str(rank)
 return c

def reference(c):
 path=HERE/'references'/(c['id']+'.json.gz')
 if not path.exists():
  attempts=[]
  for a in dict.fromkeys([geometry.action(c),'expanded']):
   r=rt.attempt(c,None,a,timeout=90);attempts.append(rt.compact(r))
   if r['success']:break
  r=rt.compact(r);r['discovery_attempts']=attempts;save(path,r)
 return path,rt.read(path)

def run(c,basis,name,reference=None,recover=True):
 start=time.perf_counter()
 if name=='previous':
  r=previous.reduce(c,basis,'learned',reference);r['strategy']=name;return r
 theta,ordering,permutation=config(c['topology_group'],name)
 attempts=[];meta=None
 with tempfile.TemporaryDirectory(prefix='joint_policy_',dir=os.environ['TMPDIR']) as td:
  # Try the selected pair once. Retry with the native ordering and no filter.
  specs=[(geometry.action(c),theta,ordering,permutation)]
  if recover:specs += [(a,None,1,None) for a in dict.fromkeys([geometry.action(c),'native','expanded'])]
  seen=set()
  for a,parameters,o,p in specs:
   key=json.dumps([inputs.bounds(c,a),inputs.truncation(c,a),parameters,o,p])
   if key in seen:continue
   seen.add(key)
   with rt.environment():
    if parameters is not None:
     tick=time.perf_counter();seeds,meta=geometry.seeds(c,basis,inputs.bounds(c,a),parameters,inputs.truncation(c,a))
     path=Path(td)/'seeds.txt';path.write_text(''.join('F['+','.join(map(str,v))+']\n' for v in seeds))
     os.environ.update(KIRA_ML_SEEDS=str(path),KIRA_ML_SEED_AUDIT=str(Path(td)/'audit.json'))
     meta['preparation_seconds']=time.perf_counter()-tick
    r=rt.native.run(c,c['size'],'native',HERE/'unused',timeout=90,margin=0,archive=False,records=False,basis=basis,check_masters=True,scratch_cap=24*1024**2,bounds=inputs.bounds(c,a),ordering=o,permutation=p,threads=1,truncate=inputs.truncation(c,a))
    r.update(seed_action=a,sparse=parameters is not None)
    audit=Path(td)/'audit.json'
    if parameters is not None and audit.exists():r['seed_audit']={k:v for k,v in json.loads(audit.read_text()).items() if k!='used'}
    attempts.append(rt.compact(r))
   if r['success']:break
 out=dict(case=c['id'],strategy=name,success=r['success'],coefficients=r.get('coefficients',{}),attempts=attempts,fallbacks=len(attempts)-1,seed_policy=meta,reference_coefficients_supplied=False)
 if reference:rt.verify(out,reference)
 out['complete_seconds']=time.perf_counter()-start
 return out

def evaluate(c,name,phase,repetition=0):
 path=HERE/phase/(c['id']+'_'+name+'_r'+str(repetition)+'.json.gz')
 if path.exists():return rt.read(path)
 refp,ref=reference(c)
 if not ref['success']:r=dict(case=c['id'],strategy=name,success=False,reference_failure=True,complete_seconds=300)
 else:r=run(c,ref['masters'],name,refp)
 r.update(repetition=repetition,worker=os.uname().nodename);save(path,r)
 print(json.dumps(dict(case=c['id'],strategy=name,phase=phase,seconds=r['complete_seconds'],success=r['success'],fallbacks=r.get('fallbacks'))),flush=True)
 return r
