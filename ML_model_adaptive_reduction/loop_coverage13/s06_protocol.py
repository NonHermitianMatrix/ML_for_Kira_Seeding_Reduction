"""Freeze a fresh family grid, controls, model weights, and exact implementation."""
from s00_loop_common import *
from s03_cases import tree_case

def grid():
 old=prior();h=old.legacy().h;out=[]
 for L in range(1,14):
  for kind in ['vacuum_one_mass','vacuum_all_mass','propagator_massless','propagator_massive','ladder','bubble_box']:
   if L==1 and kind in ['vacuum_all_mass','bubble_box']:continue
   c=h.gen.case(kind,L,False,3131);c['scope']=kind;out.append(c)
  c=h.gen.case('vacuum_one_mass',L,False,3133)
  for p in c['definition']['propagators']:p['mass_squared']='0'
  c.update(id=f'scaleless_L{L}_h3133',scope='scaleless');out.append(c)
 for kind in ['nonplanar_box','pentagon','one_mass_box']:
  for shape in ['mixed','pinched']:
   c=h.inputs.case(kind,3137,shape,'reserved');c['scope']='other_scattering';out.append(c)
 for L in [1,2,3,6,13]:
  for kind in ['vacuum_one_mass','propagator_massless','propagator_massive']:
   c=h.gen.case(kind,L,True,3139);c['scope']='symbolic_'+kind;out.append(c)
 assert len(out)==110
 return out

def main():
 assert read(HERE/'development_checks.json')['all_gamma_exact']
 trees=[]
 for L in range(1,14):
  for shape in (['star'] if L<3 else ['star','chain'] if L==3 else ['star','chain','branched']):trees.append(tree_case(L,shape,3143))
 trees += [tree_case(L,'chain',3149,True) for L in [1,2,3,6,13]]
 old=prior();h=old.legacy().h;cases=h.inputs.module('coverage_batch_cases',PRIOR/'s03_cases.py');batches=cases.batches(3151,'reserved')
 p=dict(complete=True,trees=trees,grid=grid(),batches=batches,seconds_per_application=20,repetitions=3,grid_repetitions=1,parent_commit='ca7f5f7b40d8b865cf8932a054357766097a4a24',source_sha256={q.name:sha(q) for q in HERE.glob('s0*.py')},prior_model_sha256=sha(PRIOR/'trained_model/policy.json'),prior_basis_sha256=sha(PRIOR/'basis_registry.json'),prior_runtime_sha256=sha(PRIOR/'s02_batch_runtime.py'),methods=['integrated','previous','all_fixed'],scope='Fresh finite grid through thirteen loops, connected bubble trees, and separate two-loop learned controls. No universal integral coverage or optimality claim.',tree_check='Derived identity; exact low-loop Gamma and native checks; independent 80-digit complete-Gamma evaluations at three non-pole dimensions for reserved targets. High-loop numerical checks are not native reductions.')
 write(HERE/'protocol.json.gz',p);print(json.dumps(dict(trees=len(trees),grid=len(p['grid']),batches=len(batches))),flush=True)
if __name__=='__main__':main()
