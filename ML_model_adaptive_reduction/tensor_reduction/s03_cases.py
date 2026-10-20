"""Complete one-loop coordinates with distinct massive and off-shell profiles."""
from s00_tensor_common import *

def case(P,extra,profile,rank=2,dots=1,count=1,mass='massive',seed=0):
 n=P+extra;em=[f'p{i+1}' for i in range(n-1)];rng=random.Random(100003*profile+seed)
 rules=[]
 for i in range(n-1):
  for j in range(i,n-1):rules.append([[em[i],em[j]],str(-(10*profile+17*(i+1)) if i==j else -(profile+i+2*j+1))])
 ps=[dict(momentum='k1' if i==0 else 'k1-'+em[i-1],mass_squared=str(profile+11*(i+1)**2) if i<P and (mass=='massive' or mass=='mixed' and i%2==0) else '0') for i in range(n)]
 d=dict(loop_momenta=['k1'],external_momenta=em,propagators=ps,physical_propagators=P,top_level_sectors=[(1<<P)-1],scalarproduct_rules=rules,invariants=[],rank=n,parameters=dict(profile=profile,mass_class=mass))
 ts=[]
 for attempt in range(10000):
  a=[1]*P+[0]*extra
  for _ in range(dots):a[rng.randrange(P)]+=1
  for _ in range(rank):a[P+rng.randrange(extra)]-=1
  if a not in ts:ts.append(a)
  if len(ts)>=count:break
 # A request has distinct targets; small combinatorial pools can have fewer.
 name=f'tensor_P{P}_N{n}_{mass}_h{profile}_r{rank}_d{dots}_b{len(ts)}_s{seed}'
 return dict(id=name,group=name,topology_group=f'tensor_P{P}_N{n}_{mass}',split='development',definition=d,targets=ts,size=len(ts),scope='one_loop_tensor',shape='off_shell')

def cases(phase):
 configs=[(2,1),(2,2),(3,1),(4,1)]
 profiles={'training':7103,'validation':7301,'reserved':7507}
 out=[]
 settings={'training':[(1,0,1),(1,2,2),(2,1,2),(2,3,3),(3,1,2),(4,2,2)],'validation':[(1,3,2),(3,2,2),(4,1,2)],'reserved':[(2,2,2),(3,3,2),(4,0,1),(4,3,3)]}[phase]
 for k,(P,e) in enumerate(configs):
  for j,(r,d,b) in enumerate(settings):
   c=case(P,e,profiles[phase]+k*8+j,rank=r,dots=d,count=b,seed=200*k+j);c['split']=phase;out.append(c)
 return out
