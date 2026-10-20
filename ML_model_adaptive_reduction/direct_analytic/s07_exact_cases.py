"""A fixed physical test grid across loop orders one through thirteen."""
from s00_direct_common import *

def vacuum(L,profile,extended=False):
 masses=[profile+2,profile+7] if not extended else [profile+2,profile+7,profile+2,0]
 base=[[1,1],[2,1],[1,3],[2,-1]] if not extended else [[1,1,2,0],[2,1,1,1],[1,2,0,-2],[0,0,0,2]]
 ps=[]
 for i in range(L):
  ps.extend(dict(momentum=f'k{i+1}',mass_squared=str(m)) for m in masses)
 ts=[t*L for t in base];d=dict(loop_momenta=[f'k{i+1}' for i in range(L)],external_momenta=[],propagators=ps,physical_propagators=len(ps),top_level_sectors=[(1<<len(ps))-1],scalarproduct_rules=[],invariants=[],rank=len(ps),parameters=dict(profile=profile))
 group='extended_vacuum' if extended else 'vacuum_products';name=f'direct_{group}_L{L}_h{profile}'
 return dict(id=name,group=name,split='reserved',topology_group=group,definition=d,targets=ts,size=len(ts),test_group=group)

def cases():
 out=[vacuum(L,23011+L) for L in range(1,14)]
 vc=load('direct_vacuum_cases',current().previous().previous().HERE/'s04_cases.py')
 for shape,first,offset in [('chain',1,0),('star',3,100),('binary',4,200)]:
  for L in range(first,14):
   c=vc.vacuum_case(L,shape,23111+offset+L,count=4);c.update(test_group='connected_vacuum',split='reserved');out.append(c)
 light=load('direct_light_cases',PRIOR/'s02_cases.py')
 for j,kind in enumerate(['unequal','equal','mixed']):
  c=light.case(23211+j,kind,2,1,3);c.update(test_group='lightlike',split='reserved');out.append(c)
 tensor=load('direct_tensor_cases',ROOT/'ML_model_adaptive_reduction/tensor_reduction/s03_cases.py')
 for P,e in [(2,1),(3,1),(4,1)]:
  c=tensor.case(P,e,23311+P,rank=2,dots=1,count=3);c.update(test_group='ordinary_tensor',split='reserved');out.append(c)
 return out


def massless_vacuum(L):
 lm=[f'k{i+1}' for i in range(L)];momenta=lm+[lm[i]+'-'+lm[j] for i in range(L) for j in range(i+1,L)];N=len(momenta);ts=[[1]*N,[2]+[1]*(N-1),[-1]+[1]*(N-1)]
 d=dict(loop_momenta=lm,external_momenta=[],propagators=[dict(momentum=k,mass_squared='0') for k in momenta],physical_propagators=N,top_level_sectors=[(1<<N)-1],scalarproduct_rules=[],invariants=[],rank=N)
 name=f'direct_scaleless_vacuum_L{L}';return dict(id=name,group=name,split='reserved',topology_group='scaleless_vacuum',definition=d,targets=ts,size=len(ts),test_group='scaleless_vacuum')
