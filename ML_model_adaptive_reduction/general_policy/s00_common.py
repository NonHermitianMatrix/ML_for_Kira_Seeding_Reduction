"""Common inputs for a shared cost policy without family identifiers."""
import gzip,hashlib,importlib.util,json,math,os,re,statistics,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_adaptive_reduction/learned_seed_bounds'))
import s00_inputs as inputs
import s01_runtime as rt
ACTIONS=inputs.ACTIONS
READ=rt.read
CAP=18*1024**2

def allocated():
 return sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file())
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(d,separators=(',',':')).encode()
 if p.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
 assert len(raw)<3*1024**2 and allocated()+len(raw)+8192<CAP
 q=p.with_name(p.name+'.writing');q.write_bytes(raw);q.replace(p)
def module(name,p):return inputs.module(name,p)
def features(c):
 # Pooled counts are unchanged by a permutation of loop or propagator labels.
 x=inputs.features(c);L,E,N,P=x[:4];ts=c['targets']
 x += [N/max(1,P),P/max(1,L),x[13]/max(1,N),x[14]/max(1,P),x[6]/max(1,P),x[7]/max(1,N-P),x[15]/max(1,L),x[16]/max(1,P)]
 x += [statistics.mean(sum(a==j for a in t)/N for t in ts) for j in [-2,-1,0,1,2,3]]
 x += [math.log1p(L*(L+E)),math.log1p(P)*(1+x[6]),math.log1p(max(1,N-P))*(1+x[7])]
 return x
FEATURE_NAMES=inputs.FEATURE_NAMES+['indices_per_physical','physical_per_loop','mass_fraction','coupling_fraction','dots_per_physical','rank_per_auxiliary','loop_incidence_fraction','loop_degree_fraction']+['index_fraction_'+str(i) for i in [-2,-1,0,1,2,3]]+['log_operators','dot_region_size','numerator_region_size']

def held_out(c):
 g=c.get('topology_group','')
 return len(c['definition']['loop_momenta'])>=4 or any(k in g for k in ['vacuum_all_mass','nonplanar','pentagon'])

def cases(h):
 gen=module('general_physics',ROOT/'Kira_comparison/coverage_study/s00_cases.py');out=[]
 for L in range(1,13):
  for kind in ['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive','ladder','bubble_box']:
   if L==1 and kind in ['vacuum_all_mass','bubble_box']:continue
   c=gen.case(kind,L,False,h);c['split']='reserved';c['topology_group']=kind+'_L'+str(L)
   # Two distinct target shapes at orders supported by the native interface.
   for shape in (['dots','mixed'] if len(c['definition']['propagators'])<=31 else ['mixed']):
    d=c['definition'];P=d['physical_propagators'];N=len(d['propagators']);ts=[]
    for j in range(min(P,3)):
     a=[int(i<P) for i in range(N)];a[(h+j)%P]+=2 if shape=='dots' else 1
     if shape=='mixed' and N>P:a[P+(h+j)%(N-P)]=-1
     ts.append(a)
    out.append(dict(c,id=c['id']+'_'+shape,shape=shape,targets=ts,size=len(ts)))
 for kind in ['nonplanar_box','pentagon','one_mass_box']:
  for shape in ['dots','mixed']:
   c=inputs.case(kind,h,shape,'reserved');out.append(c)
 return out

def freeze_protocol():
 p=HERE/'protocol.json'
 if p.exists():return READ(p)
 d=dict(reserved=cases(1201),actions=ACTIONS,features=FEATURE_NAMES,seed=1201,repetitions=3,timeout=45,reference_timeout=60,
  training_sources=['ML_model_adaptive_reduction/learned_seed_bounds/training','ML_model_adaptive_reduction/portfolio_policy/training'],
  excluded_from_training_and_validation=['all loop orders >=4','the distinct-mass vacuum family with loop and total-momentum denominators','all nonplanar boxes','all pentagons'],
  splits='Train on historic training only after physical holdouts; choose global model on historic validation only after the same holdouts. Freeze before new profile 1201.',
  timing='Fresh process including imports, inference, IBP generation, algebra, exact coefficient comparison, fallback, output and exit. Master discovery reported separately.',
  implementation='Shared model. No name, signature, coordinate identity, or per-family threshold is an input or deployment rule.',
  limits=dict(study_bytes=CAP,scratch_bytes=32*1024**2,concurrency=2,tree_rss_mib=5200),parent_commit='d01ffecddd08f0da632430698ebe0c8d4c38ffbc')
 write(p,d);return d
