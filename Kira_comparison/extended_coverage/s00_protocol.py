"""Freeze broader physical inputs and resource limits before evaluation."""
import copy,gzip,hashlib,importlib.util,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(d,separators=(',',':')).encode()
 if p.suffix=='.gz':b=gzip.compress(b,mtime=0)
 used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file());assert used+len(b)+4096<12*1024**2
 assert len(b)<2*1024**2
 q=p.with_suffix('.writing');q.write_bytes(b);q.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(c):
 import sympy as sp
 for r in c['definition']['scalarproduct_rules']:r[1]=str(sp.sympify(r[1],rational=True))
 return c
def make():
 gen=module('old_coverage_inputs',ROOT/'Kira_comparison/coverage_study/s00_cases.py')
 extra=module('extra_coverage_inputs',ROOT/'Kira_comparison/generalization/s01_cases.py')
 cases=[]
 for old in gen.make():
  k=old['coverage_type'];L=old['loops'];sym=old['kinematics']=='symbolic'
  if k in ['nonplanar_box','pentagon','one_mass_box']:
   c=copy.deepcopy(old);c['definition']=extra.build(k,sym,1003);c['id']=k+'_h1003_'+old['kinematics']
  else:c=gen.case(k,L,sym,h=1002 if sym else 1001)
  if k=='propagator_massive':
   p=c['definition']['physical_propagators'];n=len(c['definition']['propagators']);a=[1]*p+[0]*(n-p);ts=[a]
   for i in range(p):
    for power in [2,3]:b=a.copy();b[i]=power;ts.append(b)
    for j in range(i):b=a.copy();b[i]=b[j]=2;ts.append(b)
   c['targets']=ts;c['size']=len(ts);c['shape']='all_dots_through_two'
  cases.append(canonical(c))
 sys.path.insert(0,str(ROOT/'ML_model_seed_selection/joint_policy'));import s00_engine as engine
 for graph in ['double_box','nonplanar_box']:
  c=engine.make(graph,1009,3,'distributed','reserved');c.update(coverage_type=graph+'_rank3',kinematics='rational');cases.append(canonical(c))
 for c in cases:
  c['loops']=len(c['definition']['loop_momenta']);c['indices']=len(c['definition']['propagators']);c['preflight']='eligible' if c['indices']<=31 else 'unsupported_index_count'
 return cases

def freeze():
 cases=make();sources={str(p.relative_to(ROOT)):sha(p) for p in HERE.glob('s0*.py')}
 for folder in ['ML_model_seed_selection/joint_policy','ML_model_seed_selection/cost_geometry','ML_model_adaptive_reduction/batch_policy','ML_model_adaptive_reduction/learned_seed_bounds','ML_model_adaptive_reduction/cost_trained_sparse_seeds','ML_model_adaptive_reduction/massless_banana']:
  for p in (ROOT/folder).glob('s*.py'):sources[str(p.relative_to(ROOT))]=sha(p)
 models={}
 for folder in ['ML_model_seed_selection/joint_policy','ML_model_seed_selection/cost_geometry','ML_model_seed_selection/cost_trained_sparse_seeds','ML_model_adaptive_reduction/batch_policy','ML_model_adaptive_reduction/learned_seed_bounds']:
  for p in (ROOT/folder/'trained_model').glob('*.json'):models[str(p.relative_to(ROOT))]=sha(p)
 protocol=dict(cases=cases,methods=['native','previous','selected'],repetitions=3,native_attempt_seconds=30,native_scratch_bytes=32*1024**2,maximum_workers=2,loop_orders=list(range(1,13)),sources=sources,models=models,
  baseline='Current exact optimized Kira executable, fixed seed bounds, no learned policy; all methods start in fresh processes and include loading, generation, elimination, exact checks and recovery.',
  reference='Expanded seeds without a supplied basis; verify with integral ordering 2 and another numerator degree using the discovered basis.',
  timing='Application receives a verified master basis. Basis discovery and the independent reference check are reported separately. Repetitions rotate method order; no speedup unless all paired runs pass.',
  limits='Finite family grid, not all possible integrals. Retain unsupported and failed cases. Stop repeats of a method after failure. Do not change models or policies after viewing results.',
  analytic='24 physical-only massless banana inputs: loops 1 through 12, rational and symbolic momentum. Compare current, previous and direct exact formula; check all coefficients against an independently implemented raising recurrence. Native high-loop speedups are not inferred.',
  scale_cases=['double_box_h1009_distributed3','nonplanar_box_h1009_distributed3','ladder_L1_h1001','propagator_massless_L2_h1001'],scale_factors=['1','3/2','2'])
 p=HERE/'protocol.json'
 if p.exists():assert read(p)==protocol
 else:write(p,protocol)
 print(json.dumps(dict(cases=len(cases),eligible=sum(c['preflight']=='eligible' for c in cases))),flush=True)
if __name__=='__main__':freeze()
