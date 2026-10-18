"""Independent kinematics for analytic decomposition and unchanged ML controls."""
from s01_common import *
import itertools,copy

def polygon(n,profile,dots=2,symbolic=False):
 E=n-1;lm=['k1'];em=['p'+str(i+1) for i in range(E)]
 momenta=['k1']+['k1-'+'-'.join(em[:j]) for j in range(1,n)]
 masses=['m'+str(j+1) if symbolic else str(2+3*j+profile%17) for j in range(n)]
 rules=[]
 for i in range(E):
  for j in range(i,E):
   v=('s'+str(i+1)+str(j+1)) if symbolic else str(-(11+profile%23+7*i) if i==j else -(1+(profile+i+j)%3))
   rules.append([[em[i],em[j]],v])
 targets=[]
 for j in range(min(3,n)):
  a=[1]*n;a[j]+=dots;targets.append(a)
 a=[1]*n
 if n>1:a[0]+=1;a[-1]+=1
 if a not in targets:targets.append(a)
 defs=dict(loop_momenta=lm,external_momenta=em,propagators=[dict(momentum=q,mass_squared=m) for q,m in zip(momenta,masses)],physical_propagators=n,top_level_sectors=[(1<<n)-1],scalarproduct_rules=rules,invariants=[[v,2] for v in masses+[v for _,v in rules]] if symbolic else [],parameters=dict(profile=profile),rank=n)
 return dict(id=f'polygon_n{n}_h{profile}_dots{dots}'+('_symbolic' if symbolic else ''),group='analytic_polygon_'+str(n),definition=defs,targets=targets,size=len(targets),shape='scalar_dots',scope='one_loop',topology_group='massive_polygon_'+str(n),split='reserved')

def cases():
 cs=[polygon(n,p,dots) for p in [2411,2417] for n in range(2,6) for dots in [1,3]]
 # Symbolic two-point cases test rational functions of masses and momentum.
 cs += [polygon(2,2423,1,True),polygon(2,2429,2,True)]
 # Independent blocks span every loop order; no claim of connected high-loop graphs.
 for L in range(2,14):
  b=polygon(2,2441+L,1+(L%3));c=h.inputs.module('analytic_families',h.BLOCK/'s01_families.py').compose([b]*L,f'analytic_bubble_product_L{L}','reserved');c['scope']='products';cs.append(c)
 old=h.inputs.module('analytic_hybrid_cases',PREVIOUS/'s02_collect.py')
 for c in old.cases(2473,'reserved'):
  c['scope']='ml_compatibility';cs.append(c)
 # Preserve untouched analytic and connected multiloop controls.
 for c in h.connected(2477,'reserved'):
  if c['topology_group'] in ['propagator_massive_L2','vacuum_all_mass_L3','vacuum_one_mass_L13']:
   c['scope']='other_compatibility';cs.append(c)
 assert len(cs)==41 and len({c['id'] for c in cs})==41
 return cs

if __name__=='__main__':write(HERE/'protocol.json',dict(cases=cases(),repetitions=3,methods=['learned','fixed','native','previous'],sources={p.name:sha(p) for p in HERE.glob('s0*.py')},prior_model_sha256=sha(PREVIOUS/'trained_model/freeze.json'),prior_expert_sha256=sha(PREVIOUS/'trained_model/expert.json'),scope='Scalar one-loop massive polygons, independent one-loop blocks through thirteen loops, and retained coupled/analytic compatibility cases. Models are unchanged; new gains are analytic.'))
