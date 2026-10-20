"""Zero-invariant two-point sectors and independent products."""
from s00_light_common import *

def case(profile,kind='unequal',rank=2,dots=1,count=3):
 n=4;em=['p','q','r'];x=profile+3;y=profile+11
 if kind=='equal':y=x
 if kind=='mixed':y=0
 if kind=='massless':x=y=0
 d=dict(loop_momenta=['k1'],external_momenta=em,propagators=[dict(momentum=m,mass_squared=str(v)) for m,v in [('k1',x),('k1-p',y),('k1-q',0),('k1-r',0)]],physical_propagators=2,top_level_sectors=[3],scalarproduct_rules=[[['p','p'],'0'],[['p','q'],str(-profile-1)],[['p','r'],str(-profile-2)],[['q','q'],str(-2*profile-7)],[['q','r'],str(-profile-3)],[['r','r'],str(-3*profile-13)]],invariants=[],rank=n,parameters=dict(profile=profile,mass_class=kind))
 rng=random.Random(profile+31*rank+13*dots);ts=[]
 for _ in range(500):
  a=[1,1,0,0]
  for i in range(dots):a[rng.randrange(2)]+=1
  for i in range(rank):a[2+rng.randrange(2)]-=1
  if a not in ts:ts.append(a)
  if len(ts)==count:break
 name=f'lightlike_{kind}_h{profile}_r{rank}_d{dots}_b{len(ts)}'
 return dict(id=name,group=name,split='development',topology_group='lightlike_'+kind,definition=d,targets=ts,size=len(ts),test_group='lightlike')

def product(c,L):
 d=copy.deepcopy(c['definition']);old=d['propagators'];d['loop_momenta']=[f'k{i+1}' for i in range(L)]
 # Physical entries precede all auxiliary entries in the combined family.
 indices=[];ps=[]
 for i in range(L):
  ids=[]
  for j in range(2):ids.append(len(ps));ps.append(dict(old[j],momentum=old[j]['momentum'].replace('k1',f'k{i+1}')))
  indices.append(ids)
 for i in range(L):
  for j in range(2,4):indices[i].append(len(ps));ps.append(dict(old[j],momentum=old[j]['momentum'].replace('k1',f'k{i+1}')))
 d.update(propagators=ps,physical_propagators=2*L,top_level_sectors=[(1<<(2*L))-1],rank=len(ps))
 ts=[]
 for t in c['targets']:
  a=[0]*len(ps)
  for ids in indices:
   for j,v in zip(ids,t):a[j]=v
  ts.append(a)
 name=c['id']+'_L'+str(L);return dict(c,id=name,group=name,definition=d,targets=ts,size=len(ts),test_group='products')
