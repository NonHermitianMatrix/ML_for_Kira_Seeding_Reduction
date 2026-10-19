"""Define the reserved timing set and the separate bounded coverage grid."""
from s00_fast_common import *

def load_physics():
 old=legacy();h=old.h;polys=h.inputs.module('fast_polygons',PRIOR/'s03_cases.py');families=h.inputs.module('fast_families',h.BLOCK/'s01_families.py')
 return old,h,polys,families

def set_case(c,scope,targets=None):
 if targets is not None:c.update(targets=targets,size=len(targets))
 c.update(scope=scope,split='reserved');return canonical(c)

def timing_cases():
 old,h,polys,families=load_physics();out=[]
 for L in range(1,14):
  for kind in ['vacuum_one_mass','propagator_massless']:
   c=h.gen.case(kind,L,False,2701+2*L);out.append(set_case(c,'finite_formula'))
  # Each copy has different masses and the same external invariants.
  blocks=[]
  for b in range(L):
   c=polys.polygon(3,2741,1);c['definition']['propagators']=[dict(p,mass_squared=str(int(p['mass_squared'])+7*b+L)) for p in c['definition']['propagators']]
   c['targets']=[[2,1,1]];c['size']=1;blocks.append(c)
  c=families.compose(blocks,f'distinct_triangles_L{L}','reserved');out.append(set_case(c,'products'))
 for L in [1,2,6,13]:
  out.append(set_case(h.gen.case('vacuum_one_mass',L,True,2753),'symbolic_formula'))
 for n in [3,4,5]:
  for index,a in enumerate([[3,2]+[1]*(n-2),[1]*(n-2)+[2,3],[2]*n]):
   c=polys.polygon(n,2777,1);c['id']=f'learned_polygon_n{n}_shape{index}';out.append(set_case(c,'recurrence',[a]))
 for delta in [1,2]:
  c=polys.polygon(2,2783,delta,True);out.append(set_case(c,'symbolic_native'))
 for i,a in enumerate([[1]*7+[-2,0],[1]*7+[0,-2],[1]*7+[-3,0],[1]*7+[0,-3],[1]*7+[-2,-1],[1]*7+[-4,0],[1]*7+[0,-4],[1]*7+[-2,-2]]):
  c=h.inputs.case('nonplanar_box',2791,'rank2','reserved');c['id']=f'nonplanar_h2791_t{i}';out.append(set_case(c,'learned_native',[a]))
 for kind,L in [('propagator_massive',2),('vacuum_all_mass',3),('ladder',2)]:
  c=h.gen.case(kind,L,False,2797);P=c['definition']['physical_propagators'];N=len(c['definition']['propagators']);a=[1]*P+[0]*(N-P);a[0]+=1;out.append(set_case(c,'native_compatibility',[a]))
 assert len(out)==65,len(out)
 return out

def audit_cases():
 old,h,polys,families=load_physics();out=[]
 for L in range(1,14):
  for kind in ['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive','ladder','bubble_box']:
   if L==1 and kind in ['vacuum_all_mass','bubble_box']:continue
   out.append(set_case(h.gen.case(kind,L,False,2801),'coverage_'+kind))
  c=h.gen.case('vacuum_one_mass',L,False,2803)
  for p in c['definition']['propagators']:p['mass_squared']='0'
  c['id']=f'scaleless_vacuum_L{L}';out.append(set_case(c,'coverage_scaleless'))
 for kind in ['nonplanar_box','pentagon','one_mass_box']:
  for shape in ['mixed','pinched']:
   c=h.inputs.case(kind,2819,shape,'reserved');out.append(set_case(c,'coverage_scattering'))
 for L in [1,2,3,6,13]:
  for kind in ['vacuum_one_mass','propagator_massless','propagator_massive']:
   out.append(set_case(h.gen.case(kind,L,True,2827),'coverage_symbolic'))
 return out

def freeze():
 assert read(HERE/'trained_model/recurrence.json')['complete'];old=legacy()
 p=dict(complete=True,timing=timing_cases(),coverage=audit_cases(),methods=['learned','fixed','previous','native'],repetitions=3,application_seconds=125,coverage_seconds=20,source_sha256={q.name:sha(q) for q in HERE.glob('s0*.py')},new_model_sha256=sha(HERE/'trained_model/recurrence.json'),prior_model_sha256=sha(old.PREVIOUS/'trained_model/freeze.json'),prior_expert_sha256=sha(old.PREVIOUS/'trained_model/expert.json'),prior_basis_sha256=sha(PRIOR/'basis_registry.json'),prior_protocol_sha256=sha(PRIOR/'test_protocol.json'),gmpy2_version='2.2.1',sympy_ground_types='python',parent_commit='e0c102c895d3bf01a47f9fa49d4ddff12f3078c7',scope='65 reserved timing requests and a separate finite coverage grid at every loop count 1 through 13. Connected and factored cases remain separate; bounded failures stay in coverage.')
 assert len({c['id'] for c in p['timing']})==len(p['timing'])
 write(HERE/'protocol.json',p);print(json.dumps(dict(timing=len(p['timing']),coverage=len(p['coverage']))),flush=True)
if __name__=='__main__':freeze()
