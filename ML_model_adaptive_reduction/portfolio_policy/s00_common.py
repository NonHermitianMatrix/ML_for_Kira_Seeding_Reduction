"""Bounded family-aware seed-cost study with exact Kira checks."""
import gzip,hashlib,importlib.util,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/learned_seed_bounds'))
import s00_inputs as inputs
import s01_runtime as rt
ACTIONS=inputs.ACTIONS

def read(p):return rt.read(p)
def allocated():
 total=0
 for directory,subdirectories,files in os.walk(HERE):
  for name in files:
   try:total+=(Path(directory)/name).stat().st_blocks*512
   except FileNotFoundError:pass
 return total
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(v,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2
 used=allocated()
 assert used+len(raw)+8192<24*1024**2,'Study storage cap'
 temporary=p.with_name(p.name+'.'+str(os.getpid())+'.writing');temporary.write_bytes(raw);temporary.replace(p)
def module(name,p):return inputs.module(name,p)
def features(c):
 x=inputs.features(c);p=c['definition']['physical_propagators'];ts=c['targets']
 x.extend([max(max(0,t[i]-1) for t in ts) if i<len(ts[0]) else 0 for i in range(16)])
 x.extend([max(max(0,-t[i]) for t in ts) if i<len(ts[0]) else 0 for i in range(24)])
 return x

def make(h,split):
 gen=module('broad_physics',ROOT/'Kira_comparison/coverage_study/s00_cases.py')
 domains=[('vacuum_one_mass',l) for l in range(1,5)]+[('vacuum_all_mass',l) for l in range(1,4)]+[('propagator_massive',l) for l in range(1,4)]+[('propagator_massless',l) for l in range(2,5)]+[('ladder',l) for l in range(1,4)]+[('bubble_box',l) for l in [2,3]]
 cases=[]
 for kind,L in domains+[('nonplanar_box',2),('double_box',2),('pentagon',1),('one_mass_box',1)]:
  if kind=='double_box':d=inputs.definition(kind,h)
  elif kind in ['nonplanar_box','pentagon','one_mass_box']:d=module('extra_physics',ROOT/'Kira_comparison/generalization/s01_cases.py').build(kind,False,h)
  else:d=gen.definition(kind,L,h)
  n=len(d['propagators']);p=d['physical_propagators']
  for shape in ['dots','mixed']:
   ts=[]
   for j in range(3):
    t=[int(i<p) for i in range(n)];i=(h+j)%p
    t[i]+=2 if shape=='dots' else 1
    if shape=='mixed' and n>p:t[p+(h+j)%(n-p)]=-1
    if t not in ts:ts.append(t)
   g=kind+'_L'+str(L);name=g+'_h'+str(h)+'_'+shape
   cases.append(dict(id=name,group=g+'_h'+str(h),topology_group=g,split=split,definition=d,targets=ts,size=len(ts),shape=shape))
 return cases

def freeze():
 p=HERE/'protocol.json'
 if p.exists():return read(p)
 v=dict(splits={s:make(h,s) for s,h in [('training',1101),('validation',1111),('reserved',1127)]},actions=ACTIONS,repetitions=5,validation_repetitions=2,
  baseline_commit='11b641689fdf0b03223f01feda083c36660c1287',binary_sha256=inputs.sha(rt.BINARY),
  timing='Fresh process, import, selection, input creation, full Kira work, exact checks, all retries, and process exit. Master discovery and independent enlarged-bounds checks reported separately.',
  controls='native bounds; per-family fixed bounds chosen on validation; previous complete application; learned cost choice with per-family validation gate',
  training='Existing training-only seed-cost records plus fresh measured training profiles. Validation and test profiles are disjoint. Graphs and target shapes overlap.',
  timeout=60,reference_timeout=90,scratch_mib=32,concurrency=2,study_cap_mib=24)
 write(p,v);return v
