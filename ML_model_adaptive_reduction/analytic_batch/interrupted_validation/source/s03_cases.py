"""Disjoint target batches and exact triangle checks."""
from s00_batch_common import *
PATTERNS=[[(2,0)],[(0,3)],[(2,1)],[(2,0),(0,2)],[(3,0),(0,3),(2,1)],[(2,0),(0,3)],[(1,0),(2,0),(3,0),(4,0)],[(1,1),(2,1),(1,2),(2,2)]]

def batches(profile,split):
 h=legacy().h;out=[]
 for kind in ['double_box','nonplanar_box']:
  for i,pattern in enumerate(PATTERNS):
   c=h.inputs.case(kind,profile,'rank2',split);ts=[[1]*7+[-a,-b] for a,b in pattern]
   c.update(id=f'batch_{kind}_h{profile}_p{i}',targets=ts,size=len(ts),shape='mixed_numerator_batch',scope='native_batch');out.append(canonical(c))
 return out

def triangle(profile,targets=None,symbolic=False):
 scale='s' if symbolic else str(-101-6*profile)
 d=dict(name='F',kind='one_scale_triangle',loop_momenta=['k1'],external_momenta=['p1','p2'],physical_propagators=3,propagators=[dict(momentum=p,mass_squared='0') for p in ['k1','k1-p1','k1-p1-p2']],invariants=[['s',2]] if symbolic else [],scalarproduct_rules=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p1','p2'],f'({scale})/2' if symbolic else str(int(scale)//2) if int(scale)%2==0 else scale+'/2']],top_level_sectors=[7],rank=3,parameters=dict(profile=profile),coefficient_field='Q(d,s)' if symbolic else 'Q(d)')
 ts=targets or [[1,1,1],[2,1,1],[1,2,1],[2,2,2],[1,0,1],[1,-1,1],[2,-2,1],[0,2,1]]
 return dict(id=f'triangle_h{profile}_'+('symbolic' if symbolic else 'rational'),group='one_scale_triangle',topology_group='one_scale_triangle',split='development',definition=d,targets=ts,size=len(ts),shape='exact_triangle',scope='exact_triangle')

def physics():
 old=legacy();return old.h,old.h.inputs.module('analytic_batch_families',old.h.BLOCK/'s01_families.py')

def reserved():
 out=batches(3053,'reserved')+batches(3061,'reserved');h,families=physics()
 novel=[[(1,2)],[(3,1)],[(2,0),(1,1),(0,2)],[(0,1),(1,1),(1,2),(1,3)]]
 for kind in ['double_box','nonplanar_box']:
  for index,pattern in enumerate(novel):
   c=h.inputs.case(kind,3067,'rank2','reserved');ts=[[1]*7+[-a,-b] for a,b in pattern]
   c.update(id=f'new_indices_{kind}_h3067_p{index}',targets=ts,size=len(ts),scope='native_batch_new_indices');out.append(canonical(c))
 for L in range(1,14):
  blocks=[triangle(3071,[[1+j%3,1 if j%3 else -1,1+j%2]]) for j in range(L)]
  c=families.compose(blocks,f'one_scale_triangle_products_L{L}','reserved');c.update(scope='triangle_products');out.append(c)
 out.append(dict(triangle(3079,symbolic=True),split='reserved'))
 for kind,L in [('vacuum_one_mass',13),('propagator_massless',13),('propagator_massive',2),('ladder',2)]:
  c=h.gen.case(kind,L,False,3083);c.update(scope='compatibility',split='reserved');out.append(c)
 return out
